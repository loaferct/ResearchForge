//! Low-memory, single-pass text normalization, quote verification, and passage extraction.

use std::fs::File;
use std::io::Read;

pub const MIN_QUOTE_CHARS: usize = 20;

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
            while j < n && (chars[j] == ' ' || chars[j] == '\t' || chars[j] == '\r') {
                j += 1;
            }
            if j < n && chars[j] == '\n' {
                j += 1;
                while j < n && (chars[j] == ' ' || chars[j] == '\t' || chars[j] == '\r') {
                    j += 1;
                }
                i = j;
                continue;
            }
        }

        // 2. Map dashes & quotes
        let mapped = match c {
            '\u{2010}' | '\u{2011}' | '\u{2012}' | '\u{2013}' | '\u{2014}' | '\u{2212}' => '-',
            '\u{2018}' | '\u{2019}' | '\u{201A}' | '\u{201B}' => '\'',
            '\u{201C}' | '\u{201D}' | '\u{201E}' | '\u{201F}' => '"',
            '\u{FB01}' => {
                if !last_was_space {
                    out.push_str("fi");
                }
                i += 1;
                continue;
            }
            '\u{FB02}' => {
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

    if out.ends_with(' ') {
        out.pop();
    }
    out
}

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
        .split('…')
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

        let mut ctx_start = start.saturating_sub(context);
        while ctx_start > 0 && !text.is_char_boundary(ctx_start) {
            ctx_start -= 1;
        }

        let mut ctx_end = (end + context).min(text.len());
        while ctx_end < text.len() && !text.is_char_boundary(ctx_end) {
            ctx_end += 1;
        }

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
            location: format!("p. {page}"),
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

        if is_section_heading(trimmed) {
            outline.push(OutlineItem {
                heading: trimmed.to_string(),
                location: format!("p. {page}"),
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
    fn test_passages() {
        let text = "[[page 1]]\nIntroductory text here.\n[[page 2]]\nWe collect new dataset results here.";
        let p = find_passages(text, "dataset", 20, 5);
        assert_eq!(p.len(), 1);
        assert_eq!(p[0].location, "p. 2");
        assert!(p[0].passage.contains("dataset"));
    }
}
