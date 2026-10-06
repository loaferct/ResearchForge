//! High-performance, low-memory core algorithms and harness engine for ResearchForge.
//! Built with zero external dependencies to minimize compilation time, binary size, and RAM overhead.

pub mod ffi;
pub mod harness;
pub mod json;
pub mod literature;
pub mod text;
pub mod workspace;

// Re-exports of public Rust API
pub use ffi::*;
pub use harness::*;
pub use json::*;
pub use literature::*;
pub use text::*;
pub use workspace::*;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_core_smoke() {
        assert_eq!(
            normalize("mem-\nory  “cache” — fast"),
            "memory \"cache\" - fast"
        );
        assert!(quote_in(
            "reduce KV cache memory by 5x",
            "We reduce KV cache\nmemory by 5x while"
        ));
        assert_eq!(
            query_terms("How does the KV-cache eviction work?"),
            vec!["kv-cache", "eviction", "work"]
        );
        assert_eq!(
            short_tool("mcp__researchforge__search_papers"),
            "search_papers"
        );
    }
}
