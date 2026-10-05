#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Building researchforge_core Rust library (zero dependencies, release mode)..."
cargo build --release --manifest-path "${ROOT_DIR}/crates/researchforge_core/Cargo.toml"

LIB_SO="${ROOT_DIR}/crates/researchforge_core/target/release/libresearchforge_core.so"
DEST_SO="${ROOT_DIR}/src/researchforge/libresearchforge_core.so"

if [ -f "${LIB_SO}" ]; then
    cp -f "${LIB_SO}" "${DEST_SO}"
    echo "✓ Installed ${DEST_SO}"
elif [ -f "${ROOT_DIR}/crates/researchforge_core/target/release/libresearchforge_core.dylib" ]; then
    cp -f "${ROOT_DIR}/crates/researchforge_core/target/release/libresearchforge_core.dylib" "${ROOT_DIR}/src/researchforge/libresearchforge_core.dylib"
    echo "✓ Installed dylib"
fi
echo "Done!"
