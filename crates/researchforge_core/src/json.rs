//! Zero-dependency JSON parser, serializer, and summarizer.
//! Designed for low-memory, high-throughput parsing of JSON and JSONL event streams.

pub fn escape_json(s: &str) -> String {
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

pub fn summarize_str(text: &str, limit: usize) -> String {
    let count = text.chars().count();
    if count <= limit {
        text.to_string()
    } else {
        let truncated: String = text.chars().take(limit).collect();
        format!("{truncated}…")
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum JsonValue {
    Null,
    Bool(bool),
    Number(f64),
    String(String),
    Array(Vec<JsonValue>),
    Object(Vec<(String, JsonValue)>),
}

impl JsonValue {
    pub fn parse(input: &str) -> Result<Self, &'static str> {
        let mut parser = JsonParser::new(input.as_bytes());
        let val = parser.parse_value()?;
        parser.skip_whitespace();
        Ok(val)
    }

    pub fn get(&self, key: &str) -> Option<&JsonValue> {
        if let JsonValue::Object(map) = self {
            map.iter().find(|(k, _)| k == key).map(|(_, v)| v)
        } else {
            None
        }
    }

    pub fn as_str(&self) -> Option<&str> {
        if let JsonValue::String(s) = self {
            Some(s)
        } else {
            None
        }
    }

    pub fn as_f64(&self) -> Option<f64> {
        if let JsonValue::Number(n) = self {
            Some(*n)
        } else {
            None
        }
    }

    pub fn as_bool(&self) -> Option<bool> {
        if let JsonValue::Bool(b) = self {
            Some(*b)
        } else {
            None
        }
    }

    pub fn as_array(&self) -> Option<&[JsonValue]> {
        if let JsonValue::Array(a) = self {
            Some(a)
        } else {
            None
        }
    }

    pub fn as_object(&self) -> Option<&[(String, JsonValue)]> {
        if let JsonValue::Object(o) = self {
            Some(o)
        } else {
            None
        }
    }

    pub fn to_json_string(&self) -> String {
        let mut out = String::new();
        self.write_json(&mut out);
        out
    }

    fn write_json(&self, out: &mut String) {
        match self {
            JsonValue::Null => out.push_str("null"),
            JsonValue::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            JsonValue::Number(n) => {
                if n.fract() == 0.0 && n.abs() < 1e16 {
                    out.push_str(&format!("{}", *n as i64));
                } else {
                    out.push_str(&format!("{n}"));
                }
            }
            JsonValue::String(s) => {
                out.push('"');
                out.push_str(&escape_json(s));
                out.push('"');
            }
            JsonValue::Array(items) => {
                out.push('[');
                for (i, it) in items.iter().enumerate() {
                    if i > 0 {
                        out.push_str(", ");
                    }
                    it.write_json(out);
                }
                out.push(']');
            }
            JsonValue::Object(pairs) => {
                out.push('{');
                for (i, (k, v)) in pairs.iter().enumerate() {
                    if i > 0 {
                        out.push_str(", ");
                    }
                    out.push('"');
                    out.push_str(&escape_json(k));
                    out.push_str("\": ");
                    v.write_json(out);
                }
                out.push('}');
            }
        }
    }

    pub fn summarize(&self, limit: usize) -> String {
        match self {
            JsonValue::String(s) => summarize_str(s, limit),
            other => summarize_str(&other.to_json_string(), limit),
        }
    }
}

pub struct JsonParser<'a> {
    chars: &'a [u8],
    pos: usize,
}

impl<'a> JsonParser<'a> {
    pub fn new(input: &'a [u8]) -> Self {
        Self { chars: input, pos: 0 }
    }

    pub fn skip_whitespace(&mut self) {
        while self.pos < self.chars.len() {
            match self.chars[self.pos] {
                b' ' | b'\t' | b'\r' | b'\n' => self.pos += 1,
                _ => break,
            }
        }
    }

    fn peek(&mut self) -> Option<u8> {
        self.skip_whitespace();
        if self.pos < self.chars.len() {
            Some(self.chars[self.pos])
        } else {
            None
        }
    }

    pub fn parse_value(&mut self) -> Result<JsonValue, &'static str> {
        self.skip_whitespace();
        match self.peek() {
            Some(b'"') => self.parse_string().map(JsonValue::String),
            Some(b'{') => self.parse_object().map(JsonValue::Object),
            Some(b'[') => self.parse_array().map(JsonValue::Array),
            Some(b't') | Some(b'f') => self.parse_bool().map(JsonValue::Bool),
            Some(b'n') => self.parse_null().map(|_| JsonValue::Null),
            Some(b'-') | Some(b'+') | Some(b'0'..=b'9') => self.parse_number().map(JsonValue::Number),
            _ => Err("unexpected token"),
        }
    }

    fn parse_string(&mut self) -> Result<String, &'static str> {
        if self.pos >= self.chars.len() || self.chars[self.pos] != b'"' {
            return Err("expected quote");
        }
        self.pos += 1;
        let mut s = String::new();
        let mut start = self.pos;
        while self.pos < self.chars.len() {
            let b = self.chars[self.pos];
            if b == b'"' {
                if self.pos > start {
                    let chunk = std::str::from_utf8(&self.chars[start..self.pos])
                        .map_err(|_| "invalid utf-8")?;
                    s.push_str(chunk);
                }
                self.pos += 1;
                return Ok(s);
            } else if b == b'\\' {
                if self.pos > start {
                    let chunk = std::str::from_utf8(&self.chars[start..self.pos])
                        .map_err(|_| "invalid utf-8")?;
                    s.push_str(chunk);
                }
                self.pos += 1;
                if self.pos >= self.chars.len() {
                    return Err("unexpected end in escape");
                }
                match self.chars[self.pos] {
                    b'"' => s.push('"'),
                    b'\\' => s.push('\\'),
                    b'/' => s.push('/'),
                    b'b' => s.push('\x08'),
                    b'f' => s.push('\x0c'),
                    b'n' => s.push('\n'),
                    b'r' => s.push('\r'),
                    b't' => s.push('\t'),
                    b'u' => {
                        self.pos += 1;
                        if self.pos + 4 > self.chars.len() {
                            return Err("truncated unicode escape");
                        }
                        let hex_str = std::str::from_utf8(&self.chars[self.pos..self.pos + 4])
                            .map_err(|_| "invalid hex utf8")?;
                        let code = u32::from_str_radix(hex_str, 16)
                            .map_err(|_| "invalid hex value")?;
                        self.pos += 4;
                        if let Some(ch) = char::from_u32(code) {
                            s.push(ch);
                        } else {
                            s.push('\u{FFFD}');
                        }
                        start = self.pos;
                        continue;
                    }
                    other => s.push(other as char),
                }
                self.pos += 1;
                start = self.pos;
            } else {
                self.pos += 1;
            }
        }
        Err("unterminated string")
    }

    fn parse_number(&mut self) -> Result<f64, &'static str> {
        self.skip_whitespace();
        let start = self.pos;
        if self.pos < self.chars.len() && (self.chars[self.pos] == b'-' || self.chars[self.pos] == b'+') {
            self.pos += 1;
        }
        while self.pos < self.chars.len() {
            let b = self.chars[self.pos];
            if b.is_ascii_digit() || b == b'.' || b == b'e' || b == b'E' || b == b'+' || b == b'-' {
                self.pos += 1;
            } else {
                break;
            }
        }
        if self.pos == start {
            return Err("expected number");
        }
        let num_str = std::str::from_utf8(&self.chars[start..self.pos]).map_err(|_| "invalid number utf8")?;
        num_str.parse::<f64>().map_err(|_| "invalid number format")
    }

    fn parse_bool(&mut self) -> Result<bool, &'static str> {
        self.skip_whitespace();
        if self.chars[self.pos..].starts_with(b"true") {
            self.pos += 4;
            Ok(true)
        } else if self.chars[self.pos..].starts_with(b"false") {
            self.pos += 5;
            Ok(false)
        } else {
            Err("invalid bool")
        }
    }

    fn parse_null(&mut self) -> Result<(), &'static str> {
        self.skip_whitespace();
        if self.chars[self.pos..].starts_with(b"null") {
            self.pos += 4;
            Ok(())
        } else {
            Err("invalid null")
        }
    }

    fn parse_array(&mut self) -> Result<Vec<JsonValue>, &'static str> {
        self.pos += 1; // skip '['
        let mut arr = Vec::new();
        self.skip_whitespace();
        if self.peek() == Some(b']') {
            self.pos += 1;
            return Ok(arr);
        }
        loop {
            let val = self.parse_value()?;
            arr.push(val);
            self.skip_whitespace();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b']') => {
                    self.pos += 1;
                    return Ok(arr);
                }
                _ => return Err("expected ',' or ']' in array"),
            }
        }
    }

    fn parse_object(&mut self) -> Result<Vec<(String, JsonValue)>, &'static str> {
        self.pos += 1; // skip '{'
        let mut obj = Vec::new();
        self.skip_whitespace();
        if self.peek() == Some(b'}') {
            self.pos += 1;
            return Ok(obj);
        }
        loop {
            self.skip_whitespace();
            if self.peek() != Some(b'"') {
                return Err("expected string key in object");
            }
            let key = self.parse_string()?;
            self.skip_whitespace();
            if self.peek() != Some(b':') {
                return Err("expected ':' after object key");
            }
            self.pos += 1; // skip ':'
            let val = self.parse_value()?;
            obj.push((key, val));
            self.skip_whitespace();
            match self.peek() {
                Some(b',') => {
                    self.pos += 1;
                }
                Some(b'}') => {
                    self.pos += 1;
                    return Ok(obj);
                }
                _ => return Err("expected ',' or '}' in object"),
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_primitives() {
        assert_eq!(JsonValue::parse("null").unwrap(), JsonValue::Null);
        assert_eq!(JsonValue::parse("true").unwrap(), JsonValue::Bool(true));
        assert_eq!(JsonValue::parse("false").unwrap(), JsonValue::Bool(false));
        assert_eq!(JsonValue::parse("123.45").unwrap(), JsonValue::Number(123.45));
        assert_eq!(JsonValue::parse("-42").unwrap(), JsonValue::Number(-42.0));
        assert_eq!(
            JsonValue::parse("\"hello \\\"world\\\"\\n\"").unwrap(),
            JsonValue::String("hello \"world\"\n".to_string())
        );
    }

    #[test]
    fn test_parse_complex() {
        let json_str = r#"{"type": "tool_call", "count": 3, "items": ["a", "b"], "active": true}"#;
        let v = JsonValue::parse(json_str).unwrap();
        assert_eq!(v.get("type").and_then(|x| x.as_str()), Some("tool_call"));
        assert_eq!(v.get("count").and_then(|x| x.as_f64()), Some(3.0));
        assert_eq!(v.get("active").and_then(|x| x.as_bool()), Some(true));
        let items = v.get("items").and_then(|x| x.as_array()).unwrap();
        assert_eq!(items.len(), 2);
    }

    #[test]
    fn test_summarize() {
        assert_eq!(summarize_str("short", 10), "short");
        assert_eq!(summarize_str("1234567890extra", 10), "1234567890…");
        let v = JsonValue::String("hello world this is long".to_string());
        assert_eq!(v.summarize(5), "hello…");
    }
}
