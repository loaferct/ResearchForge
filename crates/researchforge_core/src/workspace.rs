//! High-performance workspace filesystem scanning and state snapshotting.
//! Provides near-zero RAM inspection of project directories without loading full Python models.

use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::path::Path;

use crate::json::{escape_json, JsonValue};

fn count_non_empty_lines(path: &Path) -> usize {
    if let Ok(file) = File::open(path) {
        use std::io::BufRead;
        let reader = std::io::BufReader::new(file);
        reader.lines().map_while(Result::ok).filter(|l| !l.trim().is_empty()).count()
    } else {
        0
    }
}

fn count_non_empty_json_files(dir: &Path) -> usize {
    if let Ok(entries) = std::fs::read_dir(dir) {
        entries
            .flatten()
            .filter(|e| {
                let p = e.path();
                p.is_file()
                    && p.extension().and_then(|s| s.to_str()) == Some("json")
                    && p.metadata().map(|m| m.len() > 0).unwrap_or(false)
            })
            .count()
    } else {
        0
    }
}

fn count_evaluation_files(results_dir: &Path) -> usize {
    if let Ok(entries) = std::fs::read_dir(results_dir) {
        entries
            .flatten()
            .filter(|e| {
                let p = e.path();
                p.is_file()
                    && p.file_name()
                        .and_then(|n| n.to_str())
                        .map(|s| s.ends_with(".evaluation.json"))
                        .unwrap_or(false)
            })
            .count()
    } else {
        0
    }
}

fn read_recorded_at(path: &Path) -> Option<String> {
    if !path.is_file() {
        return None;
    }
    let content = std::fs::read_to_string(path).ok()?;
    if content.trim().is_empty() {
        return None;
    }
    let json = JsonValue::parse(&content).ok()?;
    json.get("recorded_at").and_then(|v| v.as_str()).map(|s| {
        if let Some(stripped) = s.strip_suffix('Z') {
            format!("{stripped}+00:00")
        } else {
            s.to_string()
        }
    })
}

fn check_idea_yaml(path: &Path) -> bool {
    if !path.is_file() {
        return false;
    }
    let content = match std::fs::read_to_string(path) {
        Ok(c) => c,
        Err(_) => return false,
    };
    for line in content.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("analysis:") && trimmed != "analysis: null" && trimmed != "analysis: ~" {
            return true;
        }
    }
    false
}

pub fn workspace_snapshot(root_path: &str) -> Option<String> {
    let root = Path::new(root_path);
    if !root.exists() {
        return None;
    }

    // 1. Papers & relevance >= 0.2
    let papers_dir = root.join("papers");
    let mut papers = 0;
    let mut relevant_papers = 0;
    if let Ok(entries) = std::fs::read_dir(&papers_dir) {
        for entry in entries.flatten() {
            let p = entry.path();
            if p.is_file() && p.extension().and_then(|s| s.to_str()) == Some("json") {
                papers += 1;
                if let Ok(content) = std::fs::read_to_string(&p) {
                    if let Ok(json) = JsonValue::parse(&content) {
                        let rel = json.get("relevance").and_then(|v| v.as_f64()).unwrap_or(0.0);
                        if rel >= 0.2 {
                            relevant_papers += 1;
                        }
                    }
                }
            }
        }
    }

    // 2. Searches from search_log.jsonl
    let searches = count_non_empty_lines(&root.join("search_log.jsonl"));

    // 3. Analyses from papers/analyses
    let analyses = count_non_empty_json_files(&root.join("papers").join("analyses"));

    // 4. Claims & verified claims from evidence/claims
    let claims_dir = root.join("evidence").join("claims");
    let mut claims = 0;
    let mut verified_claims = 0;
    if let Ok(entries) = std::fs::read_dir(&claims_dir) {
        for entry in entries.flatten() {
            let p = entry.path();
            if p.is_file() && p.extension().and_then(|s| s.to_str()) == Some("json") {
                if let Ok(content) = std::fs::read_to_string(&p) {
                    if content.trim().is_empty() {
                        continue;
                    }
                    claims += 1;
                    if let Ok(json) = JsonValue::parse(&content) {
                        if let Some(ev_arr) = json.get("evidence").and_then(|v| v.as_array()) {
                            let any_verified = ev_arr.iter().any(|item| {
                                item.get("verified").and_then(|v| v.as_bool()) == Some(true)
                            });
                            if any_verified {
                                verified_claims += 1;
                            }
                        }
                    }
                }
            }
        }
    }

    // 5. Landscape & Critique recorded_at
    let landscape = read_recorded_at(&root.join("hypotheses").join("landscape.json"));
    let critique = read_recorded_at(&root.join("hypotheses").join("critique.json"));

    // 6. Gaps, no_gap, modifications, directions
    let gaps = count_non_empty_json_files(&root.join("hypotheses").join("gaps"));
    let no_gap = root.join("hypotheses").join("no_gap.json").is_file();
    let modifications = count_non_empty_json_files(&root.join("hypotheses").join("modifications"));
    let directions = count_non_empty_json_files(&root.join("hypotheses").join("directions"));

    // 7. Plans & evaluations
    let plans = count_non_empty_json_files(&root.join("experiments").join("plans"));
    let evaluations = count_evaluation_files(&root.join("results"));

    // 8. Idea & Plan
    let idea = check_idea_yaml(&root.join("idea.yaml"));
    let plan = root.join("hypotheses").join("investigation_plan.json").is_file();

    // 9. Uncertainties & contradicted
    let uncertainties_dir = root.join("hypotheses").join("uncertainties");
    let mut uncertainties: Vec<(String, String)> = Vec::new();
    let mut contradicted = 0;
    if let Ok(entries) = std::fs::read_dir(&uncertainties_dir) {
        let mut files: Vec<std::path::PathBuf> = entries
            .flatten()
            .map(|e| e.path())
            .filter(|p| p.is_file() && p.extension().and_then(|s| s.to_str()) == Some("json"))
            .collect();
        files.sort();
        for p in files {
            if let Ok(content) = std::fs::read_to_string(&p) {
                if content.trim().is_empty() {
                    continue;
                }
                if let Ok(json) = JsonValue::parse(&content) {
                    let id = json.get("id").and_then(|v| v.as_str()).unwrap_or("").to_string();
                    let status = json.get("status").and_then(|v| v.as_str()).unwrap_or("").to_string();
                    let has_contra_papers = json
                        .get("contradicting_paper_ids")
                        .and_then(|v| v.as_array())
                        .map(|a| !a.is_empty())
                        .unwrap_or(false);
                    let verdict = json.get("challenge_verdict").and_then(|v| v.as_str()).unwrap_or("");
                    let is_contra = has_contra_papers || verdict == "weakened" || verdict == "refuted";
                    if is_contra {
                        contradicted += 1;
                    }
                    if !id.is_empty() {
                        uncertainties.push((id, status));
                    }
                }
            }
        }
    }

    let mut json = String::new();
    json.push_str("{\"papers\":");
    json.push_str(&papers.to_string());
    json.push_str(",\"relevant_papers\":");
    json.push_str(&relevant_papers.to_string());
    json.push_str(",\"searches\":");
    json.push_str(&searches.to_string());
    json.push_str(",\"analyses\":");
    json.push_str(&analyses.to_string());
    json.push_str(",\"claims\":");
    json.push_str(&claims.to_string());
    json.push_str(",\"verified_claims\":");
    json.push_str(&verified_claims.to_string());

    json.push_str(",\"landscape\":");
    if let Some(ref l) = landscape {
        json.push('"');
        json.push_str(&escape_json(l));
        json.push('"');
    } else {
        json.push_str("null");
    }

    json.push_str(",\"critique\":");
    if let Some(ref c) = critique {
        json.push('"');
        json.push_str(&escape_json(c));
        json.push('"');
    } else {
        json.push_str("null");
    }

    json.push_str(",\"gaps\":");
    json.push_str(&gaps.to_string());
    json.push_str(",\"no_gap\":");
    json.push_str(if no_gap { "true" } else { "false" });
    json.push_str(",\"modifications\":");
    json.push_str(&modifications.to_string());
    json.push_str(",\"directions\":");
    json.push_str(&directions.to_string());
    json.push_str(",\"plans\":");
    json.push_str(&plans.to_string());
    json.push_str(",\"evaluations\":");
    json.push_str(&evaluations.to_string());
    json.push_str(",\"idea\":");
    json.push_str(if idea { "true" } else { "false" });
    json.push_str(",\"plan\":");
    json.push_str(if plan { "true" } else { "false" });

    json.push_str(",\"uncertainties\":[");
    for (i, (uid, status)) in uncertainties.iter().enumerate() {
        if i > 0 {
            json.push(',');
        }
        json.push_str("[\"");
        json.push_str(&escape_json(uid));
        json.push_str("\",\"");
        json.push_str(&escape_json(status));
        json.push_str("\"]");
    }
    json.push(']');

    json.push_str(",\"contradicted\":");
    json.push_str(&contradicted.to_string());
    json.push('}');

    Some(json)
}

pub fn papers_since_critique(root_path: &str, critique_recorded_at: &str) -> usize {
    let papers_dir = Path::new(root_path).join("papers");
    let mut count = 0;
    if let Ok(entries) = std::fs::read_dir(papers_dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("json") {
                if let Ok(content) = std::fs::read_to_string(&path) {
                    if let Ok(json) = JsonValue::parse(&content) {
                        if let Some(retrieved_at) = json.get("retrieved_at").and_then(|v| v.as_str()) {
                            if retrieved_at > critique_recorded_at {
                                count += 1;
                            }
                        }
                    }
                }
            }
        }
    }
    count
}

pub fn verified_cites(root_path: &str) -> Option<String> {
    let claims_dir = Path::new(root_path).join("evidence").join("claims");
    let mut counts: HashMap<String, usize> = HashMap::new();
    if let Ok(entries) = std::fs::read_dir(claims_dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() && path.extension().and_then(|s| s.to_str()) == Some("json") {
                if let Ok(content) = std::fs::read_to_string(&path) {
                    if content.trim().is_empty() {
                        continue;
                    }
                    if let Ok(json) = JsonValue::parse(&content) {
                        if let Some(evidence) = json.get("evidence").and_then(|v| v.as_array()) {
                            let mut seen_in_claim = HashSet::new();
                            for item in evidence {
                                if item.get("verified").and_then(|v| v.as_bool()) == Some(true) {
                                    if let Some(pid) = item.get("paper_id").and_then(|v| v.as_str()) {
                                        if !pid.is_empty() && seen_in_claim.insert(pid.to_string()) {
                                            *counts.entry(pid.to_string()).or_insert(0) += 1;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    let mut json = String::from("{");
    let mut first = true;
    for (pid, cnt) in counts.iter() {
        if !first {
            json.push(',');
        }
        first = false;
        json.push('"');
        json.push_str(&escape_json(pid));
        json.push_str("\":");
        json.push_str(&cnt.to_string());
    }
    json.push('}');
    Some(json)
}

pub fn count_papers(root_path: &str) -> usize {
    let papers_dir = Path::new(root_path).join("papers");
    if let Ok(entries) = std::fs::read_dir(papers_dir) {
        entries
            .flatten()
            .filter(|e| e.path().is_file() && e.path().extension().and_then(|s| s.to_str()) == Some("json"))
            .count()
    } else {
        0
    }
}

pub fn count_searches(root_path: &str) -> usize {
    count_non_empty_lines(&Path::new(root_path).join("search_log.jsonl"))
}

pub fn count_claims(root_path: &str) -> usize {
    count_non_empty_json_files(&Path::new(root_path).join("evidence").join("claims"))
}

pub fn load_results_json(path_str: &str) -> Option<String> {
    let path = Path::new(path_str);
    if !path.is_file() {
        return None;
    }
    use std::io::BufRead;
    let file = File::open(path).ok()?;
    let reader = std::io::BufReader::new(file);
    let mut map: HashMap<String, String> = HashMap::new();
    for line in reader.lines().map_while(Result::ok) {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        if let Ok(json) = JsonValue::parse(trimmed) {
            if let Some(key) = json.get("key").and_then(|v| v.as_str()) {
                map.insert(key.to_string(), trimmed.to_string());
            }
        }
    }
    let mut out = String::from("{");
    let mut first = true;
    for (k, row_json) in map.iter() {
        if !first {
            out.push(',');
        }
        first = false;
        out.push('"');
        out.push_str(&escape_json(k));
        out.push_str("\":");
        out.push_str(row_json);
    }
    out.push('}');
    Some(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_count_non_empty_lines() {
        let tmp = std::env::temp_dir().join("test_rf_lines.txt");
        std::fs::write(&tmp, "line1\n\nline2\n   \nline3\n").unwrap();
        assert_eq!(count_non_empty_lines(&tmp), 3);
        let _ = std::fs::remove_file(tmp);
    }
}
