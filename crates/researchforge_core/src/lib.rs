//! High-performance, low-memory core algorithms for ResearchForge.
//! Built with zero external dependencies to minimize compilation time, binary size, and RAM overhead.

use std::collections::HashSet;
use std::ffi::{CStr, CString};
use std::fs::File;
use std::io::Read;
use std::os::raw::c_char;

// -----------------------------------------------------------------------------
// Stop words & Constants
// -----------------------------------------------------------------------------

const STOP_WORDS: &[&str] = &[
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from",
    "how", "in", "into", "is", "it", "of", "on", "or", "that", "the", "this",
    "to", "via", "what", "when", "which", "while", "with", "without",
    "does", "do", "we", "our", "using", "use", "based", "towards", "toward",
];

const MIN_QUOTE_CHARS: usize = 20;

// -----------------------------------------------------------------------------
// Text Normalization (Low-Memory, Single-Pass)
// -----------------------------------------------------------------------------

/// Normalizes text for quote verification and text matching.
/// Replaces typographical dashes with '-', smart quotes with '\'' / '"',
/// de-hyphenates PDF line breaks ("-\s*\n\s*"), collapses whitespace, and lowercases.
pub fn normalize(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let chars: Vec<char> = text.chars().collect();
    let n = chars.len();
    let mut i = 0;
    let mut last_was_space = true; // suppresses leading spaces

    while i < n {
        let c = chars[i];

        // 1. Check for hyphen line break: "-\s*\n\s*"
        let is_hyphen = c == '-'
            || c == '\u{2010}'
            || c == '\u{2011}'
            || c == '\u{2012}'
            || c == '\u{2013}'
            || c == '\u{2014}'
            || c == '\u{2212}';

        if is_hyphen {
            let mut j = i + 1;
            // scan optional spaces before newline
            while j < n && (chars[j] == ' ' || chars[j] == '\t' || chars[j] == '\r') {
                j += 1;
            }
            if j < n && chars[j] == '\n' {
                j += 1;
                // scan optional spaces after newline
                while j < n && (chars[j] == ' ' || chars[j] == '\t' || chars[j] == '\r') {
                    j += 1;
                }
                // Skip the hyphen and the line break
                i = j;
                continue;
            }
        }

        // 2. Map dashes & quotes
        let mapped = match c {
            '\u{2010}' | '\u{2011}' | '\u{2012}' | '\u{2013}' | '\u{2014}' | '\u{2212}' => '-',
            '\u{2018}' | '\u{2019}' | '\u{201A}' | '\u{201B}' => '\'',
            '\u{201C}' | '\u{201D}' | '\u{201E}' | '\u{201F}' => '"',
            // Unicode ligatures common in PDFs
            '\u{FB01}' => {
                // fi
                if !last_was_space {
                    out.push_str("fi");
                }
                i += 1;
                continue;
            }
            '\u{FB02}' => {
                // fl
                if !last_was_space {
                    out.push_str("fl");
                }
                i += 1;
                continue;
            }
            _ => c,
        };

        // 3. Whitespace collapsing & lowercasing
        if mapped.is_whitespace() {
            if !last_was_space {
                out.push(' ');
                last_was_space = true;
            }
        } else {
            for lc in mapped.to_lowercase() {
                out.push(lc);
            }
            last_was_space = false;
        }

        i += 1;
    }

    // Strip trailing space if any
    if out.ends_with(' ') {
        out.pop();
    }
    out
}

// -----------------------------------------------------------------------------
// Quote Verification
// -----------------------------------------------------------------------------

/// Check if `quote` appears verbatim or via ellipsis fragments in `haystack`.
pub fn quote_in(quote: &str, haystack: &str) -> bool {
    let q_norm = normalize(quote);
    let q = q_norm.trim_matches(&[' ', '.', ',', ';', ':', '"', '\''][..]);
    if q.chars().count() < MIN_QUOTE_CHARS {
        return false;
    }

    let h = normalize(haystack);
    if h.contains(q) {
        return true;
    }

    // Tolerate ellipses: every fragment must appear, in order.
    let parts: Vec<&str> = q
        .split(|c| c == '…')
        .flat_map(|s| s.split("..."))
        .map(|p| p.trim_matches(&[' ', '.', ',', ';', ':'][..]))
        .filter(|p| !p.is_empty())
        .collect();

    if parts.len() > 1 && parts.iter().all(|p| p.chars().count() >= 8) {
        let mut pos = 0;
        for p in parts {
            if let Some(idx) = h[pos..].find(p) {
                pos += idx + p.len();
            } else {
                return false;
            }
        }
        return true;
    }

    false
}

/// Directly check if `quote` is in a file without loading the entire text into Python memory.
pub fn quote_in_file(quote: &str, path: &str) -> bool {
    let mut file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return false,
    };
    let mut text = String::new();
    if file.read_to_string(&mut text).is_err() {
        return false;
    }
    quote_in(quote, &text)
}

// -----------------------------------------------------------------------------
// Literature & Query Processing
// -----------------------------------------------------------------------------

/// Extracts query terms: alphanumeric tokens (with internal hyphens), lowercased,
/// excluding stop words.
pub fn query_terms(query: &str) -> Vec<String> {
    let mut terms = Vec::new();
    let lower = query.to_lowercase();
    let chars: Vec<char> = lower.chars().collect();
    let n = chars.len();
    let mut i = 0;

    while i < n {
        if chars[i].is_ascii_alphanumeric() {
            let start = i;
            while i < n && (chars[i].is_ascii_alphanumeric() || chars[i] == '-') {
                i += 1;
            }
            let word: String = chars[start..i].iter().collect();
            let trimmed = word.trim_end_matches('-');
            if !trimmed.is_empty() && !STOP_WORDS.contains(&trimmed) {
                terms.push(trimmed.to_string());
            }
        } else {
            i += 1;
        }
    }
    terms
}

fn words(text: &str) -> HashSet<String> {
    query_terms(text).into_iter().filter(|t| t.len() > 3).collect()
}

/// Jaccard similarity of distinctive words (>3 chars) between two abstracts.
pub fn abstract_overlap(a: &str, b: &str) -> f64 {
    let wa = words(a);
    let wb = words(b);
    if wa.is_empty() || wb.is_empty() {
        return 1.0;
    }
    let intersection = wa.intersection(&wb).count();
    let union = wa.union(&wb).count();
    if union == 0 {
        1.0
    } else {
        intersection as f64 / union as f64
    }
}

/// Extracts method name from title (e.g. "H$_2$O: Heavy-Hitter..." -> "h2o").
pub fn title_name(title: &str) -> Option<String> {
    if !title.contains(':') {
        return None;
    }
    let prefix = title.split(':').next()?;
    if prefix.split_whitespace().count() > 3 {
        return None;
    }
    let name: String = prefix
        .chars()
        .filter(|c| c.is_ascii_alphanumeric())
        .map(|c| c.to_ascii_lowercase())
        .collect();
    if name.len() >= 2 {
        Some(name)
    } else {
        None
    }
}

/// Measures share of distinctive title words found in the abstract, plus 1.0 if method name appears.
pub fn title_fit(title: &str, abstract_text: &str) -> f64 {
    let wt = words(title);
    let wa = words(abstract_text);
    let mut fit = if !wt.is_empty() {
        let inter = wt.intersection(&wa).count();
        inter as f64 / wt.len() as f64
    } else {
        0.0
    };

    if let Some(name) = title_name(title) {
        let abs_norm: String = abstract_text
            .chars()
            .filter(|c| c.is_ascii_alphanumeric())
            .map(|c| c.to_ascii_lowercase())
            .collect();
        if abs_norm.contains(&name) {
            fit += 1.0;
        }
    }
    fit
}

/// Cleans title to lowercase ASCII alphanumeric key.
pub fn title_key(title: &str) -> String {
    title
        .chars()
        .filter(|c| c.is_ascii_alphanumeric())
        .map(|c| c.to_ascii_lowercase())
        .collect()
}

/// Lexical relevance score in [0, 1] given query/idea terms.
pub fn relevance(title: &str, abstract_text: &str, terms: &[String]) -> f64 {
    let mut distinct = Vec::new();
    let mut seen = HashSet::new();
    for t in terms {
        if t.len() > 2 && seen.insert(t.clone()) {
            distinct.push(t);
        }
    }
    if distinct.is_empty() {
        return 0.0;
    }

    let t_set: HashSet<String> = query_terms(title).into_iter().collect();
    let a_set: HashSet<String> = query_terms(abstract_text).into_iter().collect();

    let mut score = 0.0;
    for t in &distinct {
        if t_set.contains(*t) {
            score += 2.0;
        } else if a_set.contains(*t) {
            score += 1.0;
        }
    }

    let val = score / (2.0 * distinct.len() as f64);
    (val * 10000.0).round() / 10000.0
}

// -----------------------------------------------------------------------------
// Full-Text Passage Search & Outline Extraction
// -----------------------------------------------------------------------------

#[derive(Debug)]
pub struct Passage {
    pub location: String,
    pub passage: String,
}

/// Efficient case-insensitive search for patterns (supporting `|` alternation),
/// finding the closest preceding `[[page N]]` without duplicating prefix strings.
pub fn find_passages(text: &str, pattern: &str, context: usize, limit: usize) -> Vec<Passage> {
    let subpatterns: Vec<String> = pattern
        .split('|')
        .map(|s| s.trim().to_lowercase())
        .filter(|s| !s.is_empty())
        .collect();

    if subpatterns.is_empty() {
        return Vec::new();
    }

    let text_lower = text.to_lowercase();
    let mut match_indices = Vec::new();

    for sp in &subpatterns {
        let mut pos = 0;
        while let Some(idx) = text_lower[pos..].find(sp) {
            let actual_idx = pos + idx;
            match_indices.push((actual_idx, actual_idx + sp.len()));
            pos = actual_idx + 1;
            if pos >= text_lower.len() {
                break;
            }
        }
    }

    match_indices.sort_by_key(|&(start, _)| start);
    match_indices.dedup_by_key(|&mut (start, _)| start);

    let mut passages = Vec::new();

    for (start, end) in match_indices {
        // Find preceding page marker without slicing strings
        let page = match text[..start].rfind("[[page ") {
            Some(idx) => {
                let remainder = &text[idx + 7..];
                if let Some(close_idx) = remainder.find("]]") {
                    let page_str = &remainder[..close_idx].trim();
                    if page_str.chars().all(|c| c.is_ascii_digit()) {
                        page_str.to_string()
                    } else {
                        "?".to_string()
                    }
                } else {
                    "?".to_string()
                }
            }
            None => "?".to_string(),
        };

        // Find character-safe boundary for start
        let mut ctx_start = start.saturating_sub(context);
        while ctx_start > 0 && !text.is_char_boundary(ctx_start) {
            ctx_start -= 1;
        }

        let mut ctx_end = (end + context).min(text.len());
        while ctx_end < text.len() && !text.is_char_boundary(ctx_end) {
            ctx_end += 1;
        }

        // Collapse whitespace in context slice
        let mut cleaned = String::with_capacity(ctx_end - ctx_start);
        let mut prev_space = true;
        for c in text[ctx_start..ctx_end].chars() {
            if c.is_whitespace() {
                if !prev_space {
                    cleaned.push(' ');
                    prev_space = true;
                }
            } else {
                cleaned.push(c);
                prev_space = false;
            }
        }
        if cleaned.ends_with(' ') {
            cleaned.pop();
        }

        passages.push(Passage {
            location: format!("p. {}", page),
            passage: cleaned,
        });

        if passages.len() >= limit {
            break;
        }
    }

    passages
}

#[derive(Debug)]
pub struct OutlineItem {
    pub heading: String,
    pub location: String,
}

/// Parses line-by-line section outlines and page markers.
pub fn section_outline(text: &str, limit: usize) -> Vec<OutlineItem> {
    let mut outline = Vec::new();
    let mut page = "1".to_string();

    for line in text.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("[[page ") && trimmed.ends_with("]]") {
            let inner = &trimmed[7..trimmed.len() - 2].trim();
            if inner.chars().all(|c| c.is_ascii_digit()) {
                page = inner.to_string();
                continue;
            }
        }

        // Check heading pattern:
        // e.g. "1 Introduction", "1.2 Related Work", "A. Appendix", "3 Method"
        if is_section_heading(trimmed) {
            outline.push(OutlineItem {
                heading: trimmed.to_string(),
                location: format!("p. {}", page),
            });
            if outline.len() >= limit {
                break;
            }
        }
    }

    outline
}

fn is_section_heading(s: &str) -> bool {
    let parts: Vec<&str> = s.splitn(2, |c: char| c.is_whitespace()).collect();
    if parts.len() < 2 {
        return false;
    }
    let num_part = parts[0].trim_end_matches('.');
    let rest = parts[1].trim();

    // Check num_part:
    let is_num = if num_part.len() == 1 && num_part.chars().next().unwrap().is_ascii_uppercase() {
        let ch = num_part.chars().next().unwrap();
        ('A'..='H').contains(&ch)
    } else {
        let segments: Vec<&str> = num_part.split('.').collect();
        if segments.is_empty() || segments.len() > 2 {
            false
        } else {
            segments.iter().all(|seg| {
                !seg.is_empty()
                    && seg.len() <= 2
                    && seg.chars().all(|c| c.is_ascii_digit())
            })
        }
    };

    if !is_num {
        return false;
    }

    // Remainder: starts with uppercase, length between 2 and 60 chars, valid chars
    if rest.len() < 2 || rest.len() > 60 {
        return false;
    }
    let first = match rest.chars().next() {
        Some(c) => c,
        None => return false,
    };
    if !first.is_ascii_uppercase() {
        return false;
    }

    rest.chars().all(|c| {
        c.is_ascii_alphanumeric()
            || c.is_whitespace()
            || c == ','
            || c == ':'
            || c == '-'
    })
}

// -----------------------------------------------------------------------------
// C FFI Layer (ctypes / cffi compatible)
// -----------------------------------------------------------------------------

unsafe fn c_str_to_str<'a>(ptr: *const c_char) -> &'a str {
    if ptr.is_null() {
        ""
    } else {
        match CStr::from_ptr(ptr).to_str() {
            Ok(s) => s,
            Err(_) => "",
        }
    }
}

fn str_to_c_str(s: &str) -> *mut c_char {
    match CString::new(s) {
        Ok(cs) => cs.into_raw(),
        Err(_) => CString::new("").unwrap().into_raw(),
    }
}

#[no_mangle]
pub unsafe extern "C" fn rf_free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        drop(CString::from_raw(ptr));
    }
}

#[no_mangle]
pub unsafe extern "C" fn rf_normalize(text: *const c_char) -> *mut c_char {
    let t = c_str_to_str(text);
    let res = normalize(t);
    str_to_c_str(&res)
}

#[no_mangle]
pub unsafe extern "C" fn rf_quote_in(quote: *const c_char, haystack: *const c_char) -> bool {
    let q = c_str_to_str(quote);
    let h = c_str_to_str(haystack);
    quote_in(q, h)
}

#[no_mangle]
pub unsafe extern "C" fn rf_quote_in_file(quote: *const c_char, path: *const c_char) -> bool {
    let q = c_str_to_str(quote);
    let p = c_str_to_str(path);
    quote_in_file(q, p)
}

#[no_mangle]
pub unsafe extern "C" fn rf_abstract_overlap(a: *const c_char, b: *const c_char) -> f64 {
    let sa = c_str_to_str(a);
    let sb = c_str_to_str(b);
    abstract_overlap(sa, sb)
}

#[no_mangle]
pub unsafe extern "C" fn rf_title_fit(title: *const c_char, abstract_text: *const c_char) -> f64 {
    let t = c_str_to_str(title);
    let a = c_str_to_str(abstract_text);
    title_fit(t, a)
}

#[no_mangle]
pub unsafe extern "C" fn rf_title_name(title: *const c_char) -> *mut c_char {
    let t = c_str_to_str(title);
    match title_name(t) {
        Some(name) => str_to_c_str(&name),
        None => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub unsafe extern "C" fn rf_title_key(title: *const c_char) -> *mut c_char {
    let t = c_str_to_str(title);
    str_to_c_str(&title_key(t))
}

#[no_mangle]
pub unsafe extern "C" fn rf_query_terms_json(query: *const c_char) -> *mut c_char {
    let q = c_str_to_str(query);
    let terms = query_terms(q);
    let mut json = String::from("[");
    for (i, t) in terms.iter().enumerate() {
        if i > 0 {
            json.push(',');
        }
        json.push('"');
        json.push_str(&escape_json(t));
        json.push('"');
    }
    json.push(']');
    str_to_c_str(&json)
}

#[no_mangle]
pub unsafe extern "C" fn rf_relevance(
    title: *const c_char,
    abstract_text: *const c_char,
    terms_json: *const c_char,
) -> f64 {
    let t = c_str_to_str(title);
    let a = c_str_to_str(abstract_text);
    let tj = c_str_to_str(terms_json);

    // Simple manual parsing of JSON array of strings `["term1", "term2"]`
    let mut terms = Vec::new();
    let trimmed = tj.trim().trim_start_matches('[').trim_end_matches(']');
    for part in trimmed.split(',') {
        let p = part.trim().trim_matches('"');
        if !p.is_empty() {
            terms.push(p.to_string());
        }
    }
    relevance(t, a, &terms)
}

#[no_mangle]
pub unsafe extern "C" fn rf_find_passages_json(
    text: *const c_char,
    pattern: *const c_char,
    context: usize,
    limit: usize,
) -> *mut c_char {
    let t = c_str_to_str(text);
    let p = c_str_to_str(pattern);
    let passages = find_passages(t, p, context, limit);

    // Format JSON array: `[{"location":"p. 1","passage":"..."},...]`
    let mut json = String::from("[");
    for (i, item) in passages.iter().enumerate() {
        if i > 0 {
            json.push(',');
        }
        json.push_str("{\"location\":\"");
        json.push_str(&escape_json(&item.location));
        json.push_str("\",\"passage\":\"");
        json.push_str(&escape_json(&item.passage));
        json.push_str("\"}");
    }
    json.push(']');
    str_to_c_str(&json)
}

#[no_mangle]
pub unsafe extern "C" fn rf_section_outline_json(text: *const c_char, limit: usize) -> *mut c_char {
    let t = c_str_to_str(text);
    let outline = section_outline(t, limit);

    let mut json = String::from("[");
    for (i, item) in outline.iter().enumerate() {
        if i > 0 {
            json.push(',');
        }
        json.push_str("{\"heading\":\"");
        json.push_str(&escape_json(&item.heading));
        json.push_str("\",\"location\":\"");
        json.push_str(&escape_json(&item.location));
        json.push_str("\"}");
    }
    json.push(']');
    str_to_c_str(&json)
}

fn escape_json(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            _ => out.push(c),
        }
    }
    out
}

// -----------------------------------------------------------------------------
// Rust Unit Tests
// -----------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_normalize() {
        assert_eq!(
            normalize("mem-\nory  “cache” — fast"),
            "memory \"cache\" - fast"
        );
    }

    #[test]
    fn test_quote_in() {
        assert!(quote_in(
            "reduce KV cache memory by 5x",
            "We reduce KV cache\nmemory by 5x while"
        ));
        assert!(quote_in(
            "We reduce KV cache ... preserving accuracy on long-context",
            "We reduce KV cache memory by 5x while preserving accuracy on long-context tasks."
        ));
        assert!(!quote_in("short", "short text"));
        assert!(!quote_in(
            "reduce KV cache memory by 10x",
            "We reduce KV cache memory by 5x"
        ));
    }

    #[test]
    fn test_query_terms() {
        assert_eq!(
            query_terms("How does the KV-cache eviction work?"),
            vec!["kv-cache", "eviction", "work"]
        );
    }

    #[test]
    fn test_title_name_and_fit() {
        let title = "H$_2$O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models";
        let right_abs = "We introduce Heavy Hitter Oracle (H2O), a KV cache eviction policy that dynamically retains a balance of recent and heavy-hitter tokens, reducing the memory footprint of generative inference in large language models.";
        let wrong_abs = "Hyde-IKV is a dynamic management system for the Key-Value (KV) cache in Small Language Models (SLMs).";

        assert_eq!(title_name(title), Some("h2o".to_string()));
        assert!(title_fit(title, right_abs) > title_fit(title, wrong_abs));
    }

    #[test]
    fn test_passages() {
        let text = "[[page 1]]\nIntroductory text here.\n[[page 2]]\nWe collect new dataset results here.";
        let p = find_passages(text, "dataset", 20, 5);
        assert_eq!(p.len(), 1);
        assert_eq!(p[0].location, "p. 2");
        assert!(p[0].passage.contains("dataset"));
    }
}
