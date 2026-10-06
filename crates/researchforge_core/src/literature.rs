//! High-performance query term extraction, paper deduplication, and lexical relevance scoring.

use std::collections::HashSet;

pub const STOP_WORDS: &[&str] = &[
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for", "from",
    "how", "in", "into", "is", "it", "of", "on", "or", "that", "the", "this",
    "to", "via", "what", "when", "which", "while", "with", "without",
    "does", "do", "we", "our", "using", "use", "based", "towards", "toward",
];

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

pub fn words(text: &str) -> HashSet<String> {
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

#[cfg(test)]
mod tests {
    use super::*;

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
}
