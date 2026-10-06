//! C FFI Layer (ctypes / cffi compatible).
//! All returned strings must be freed by Python using `rf_free_string`.

#![allow(clippy::missing_safety_doc)]

use std::ffi::{CStr, CString};
use std::os::raw::c_char;

use crate::harness::{dsh_parse_event, short_tool};
use crate::json::{escape_json, summarize_str};
use crate::literature::{
    abstract_overlap, query_terms, relevance, title_fit, title_key, title_name,
};
use crate::text::{find_passages, normalize, quote_in, quote_in_file, section_outline};
use crate::workspace::{
    count_claims, count_papers, count_searches, load_results_json, papers_since_critique,
    verified_cites, workspace_snapshot,
};

pub unsafe fn c_str_to_str<'a>(ptr: *const c_char) -> &'a str {
    if ptr.is_null() {
        ""
    } else {
        CStr::from_ptr(ptr).to_str().unwrap_or_default()
    }
}

pub fn str_to_c_str(s: &str) -> *mut c_char {
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

// -----------------------------------------------------------------------------
// Harness C FFI Exports
// -----------------------------------------------------------------------------

#[no_mangle]
pub unsafe extern "C" fn rf_short_tool(name: *const c_char) -> *mut c_char {
    let n = c_str_to_str(name);
    str_to_c_str(&short_tool(n))
}

#[no_mangle]
pub unsafe extern "C" fn rf_summarize(text: *const c_char, limit: usize) -> *mut c_char {
    let t = c_str_to_str(text);
    str_to_c_str(&summarize_str(t, limit))
}

#[no_mangle]
pub unsafe extern "C" fn rf_dsh_parse_event(line: *const c_char) -> *mut c_char {
    let l = c_str_to_str(line);
    match dsh_parse_event(l) {
        Some(s) => str_to_c_str(&s),
        None => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub unsafe extern "C" fn rf_workspace_snapshot(root: *const c_char) -> *mut c_char {
    let r = c_str_to_str(root);
    match workspace_snapshot(r) {
        Some(s) => str_to_c_str(&s),
        None => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub unsafe extern "C" fn rf_papers_since_critique(
    root: *const c_char,
    recorded_at: *const c_char,
) -> usize {
    let r = c_str_to_str(root);
    let ra = c_str_to_str(recorded_at);
    papers_since_critique(r, ra)
}

#[no_mangle]
pub unsafe extern "C" fn rf_verified_cites(root: *const c_char) -> *mut c_char {
    let r = c_str_to_str(root);
    match verified_cites(r) {
        Some(s) => str_to_c_str(&s),
        None => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub unsafe extern "C" fn rf_count_papers(root: *const c_char) -> usize {
    let r = c_str_to_str(root);
    count_papers(r)
}

#[no_mangle]
pub unsafe extern "C" fn rf_count_searches(root: *const c_char) -> usize {
    let r = c_str_to_str(root);
    count_searches(r)
}

#[no_mangle]
pub unsafe extern "C" fn rf_count_claims(root: *const c_char) -> usize {
    let r = c_str_to_str(root);
    count_claims(r)
}

#[no_mangle]
pub unsafe extern "C" fn rf_load_results_json(path: *const c_char) -> *mut c_char {
    let p = c_str_to_str(path);
    match load_results_json(p) {
        Some(s) => str_to_c_str(&s),
        None => std::ptr::null_mut(),
    }
}
