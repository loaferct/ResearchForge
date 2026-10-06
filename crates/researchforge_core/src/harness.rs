//! DeepSeek Harness runtime event parsing and line processing.
//! Accelerates real-time NDJSON event streaming with zero heap allocation in Python.

use crate::json::{escape_json, summarize_str, JsonValue};

pub fn short_tool(name: &str) -> String {
    let prefix = "mcp__researchforge__";
    if let Some(stripped) = name.strip_prefix(prefix) {
        stripped.to_string()
    } else {
        name.to_string()
    }
}

pub fn dsh_parse_event(line: &str) -> Option<String> {
    let trimmed = line.trim();
    if trimmed.is_empty() {
        return None;
    }
    let ev = JsonValue::parse(trimmed).ok()?;
    let kind = ev.get("type").and_then(|v| v.as_str())?;

    let mut out = String::from("{\"kind\":\"");

    match kind {
        "session" => {
            let sid = ev.get("sessionId").and_then(|v| v.as_str());
            out.push_str("session\",\"sessionId\":");
            if let Some(s) = sid {
                out.push('"');
                out.push_str(&escape_json(s));
                out.push('"');
            } else {
                out.push_str("null");
            }
            out.push('}');
            Some(out)
        }
        "tool_call" => {
            let tool_raw = ev.get("tool").and_then(|v| v.as_str()).unwrap_or("");
            let tool = short_tool(tool_raw);
            let input_sum = ev.get("input").map(|v| v.summarize(400)).unwrap_or_default();
            out.push_str("tool_call\",\"tool\":\"");
            out.push_str(&escape_json(&tool));
            out.push_str("\",\"input\":\"");
            out.push_str(&escape_json(&input_sum));
            out.push_str("\"}");
            Some(out)
        }
        "tool_result" => {
            let status = ev.get("status").and_then(|v| v.as_str()).unwrap_or("");
            let failed = status == "error";
            let res_sum = ev.get("result").map(|v| v.summarize(600)).unwrap_or_default();
            out.push_str("tool_result\",\"status\":\"");
            out.push_str(&escape_json(status));
            out.push_str("\",\"failed\":");
            out.push_str(if failed { "true" } else { "false" });
            out.push_str(",\"result\":\"");
            out.push_str(&escape_json(&res_sum));
            out.push_str("\"}");
            Some(out)
        }
        "text" => {
            let text = ev.get("text").and_then(|v| v.as_str()).unwrap_or("");
            if text.trim().is_empty() {
                return None;
            }
            let sum = summarize_str(text, 2000);
            out.push_str("agent_text\",\"text\":\"");
            out.push_str(&escape_json(&sum));
            out.push_str("\"}");
            Some(out)
        }
        "status" => {
            let phase = ev.get("phase").and_then(|v| v.as_str()).unwrap_or("");
            if phase == "turn_end" {
                let reason = ev.get("reason");
                let finish_reason = match reason {
                    Some(JsonValue::Object(obj)) => {
                        obj.iter()
                            .find(|(k, _)| k == "kind")
                            .and_then(|(_, v)| v.as_str())
                            .map(|s| s.to_string())
                            .unwrap_or_else(|| reason.unwrap().to_json_string())
                    }
                    Some(JsonValue::String(s)) => s.clone(),
                    Some(other) => other.to_json_string(),
                    None => String::new(),
                };
                let err_sum = if finish_reason == "error" {
                    reason.map(|r| r.summarize(800))
                } else {
                    None
                };
                out.push_str("turn_end\",\"finish_reason\":\"");
                out.push_str(&escape_json(&finish_reason));
                out.push_str("\",\"error\":");
                if let Some(ref err) = err_sum {
                    out.push('"');
                    out.push_str(&escape_json(err));
                    out.push('"');
                } else {
                    out.push_str("null");
                }
                out.push('}');
                Some(out)
            } else if phase == "step_end" {
                if let Some(JsonValue::Object(usage_obj)) = ev.get("usage") {
                    out.push_str("step_end\",\"usage\":{");
                    let mut first = true;
                    for (k, v) in usage_obj {
                        if let Some(num) = v.as_f64() {
                            if !first {
                                out.push(',');
                            }
                            first = false;
                            out.push('"');
                            out.push_str(&escape_json(k));
                            out.push_str("\":");
                            out.push_str(&format!("{num}"));
                        }
                    }
                    out.push_str("}}");
                    Some(out)
                } else {
                    None
                }
            } else {
                None
            }
        }
        "final" => {
            let text = ev.get("text").and_then(|v| v.as_str()).unwrap_or("");
            out.push_str("final\",\"text\":\"");
            out.push_str(&escape_json(text));
            out.push_str("\"}");
            Some(out)
        }
        "error" => {
            let msg = if let Some(m) = ev.get("message").and_then(|v| v.as_str()) {
                m.to_string()
            } else {
                ev.summarize(400)
            };
            out.push_str("error\",\"message\":\"");
            out.push_str(&escape_json(&msg));
            out.push_str("\"}");
            Some(out)
        }
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_short_tool() {
        assert_eq!(
            short_tool("mcp__researchforge__search_papers"),
            "search_papers"
        );
        assert_eq!(short_tool("bash"), "bash");
    }

    #[test]
    fn test_dsh_parse_event() {
        let line = r#"{"type":"tool_call","tool":"mcp__researchforge__search_papers","input":{"query":"kv"}}"#;
        let res = dsh_parse_event(line).unwrap();
        assert!(res.contains("\"kind\":\"tool_call\""));
        assert!(res.contains("\"tool\":\"search_papers\""));
        assert!(res.contains("\"input\":\"{\\\"query\\\": \\\"kv\\\"}\""));

        let step = r#"{"type":"status","phase":"step_end","usage":{"inputTokens":100,"outputTokens":20}}"#;
        let step_res = dsh_parse_event(step).unwrap();
        assert!(step_res.contains("\"kind\":\"step_end\""));
        assert!(step_res.contains("\"inputTokens\":100"));
        assert!(step_res.contains("\"outputTokens\":20"));
    }
}
