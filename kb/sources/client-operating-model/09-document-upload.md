# COM · Document upload

> Source: `docs/MOON-2389 Client Operating Model.docx.pdf` pp. 33–34 · Source ID `com`

Uploading **stores** the document with the methodology and emits
`operating_model.methodology_document.uploaded`; **nothing else**. Whether/when the AI team extracts stages
and activities is OQ #14; turning extracted content into methodology changes is future phase.

## Upload: `PUT /client-methodologies/{id}/document` (pp. 33–34)
1. Check methodology exists in the tenant, is not archived, and exactly one file was sent.
2. Check size against `METHODOLOGY_DOCUMENT_MAX_BYTES` (**25 MB** proposed, same as ticket attachments). Re-check the real byte count after reading, as `ticket_import` does.
3. Detect type **from content**, never name or client MIME:
   - PDF starts with `%PDF-`.
   - DOCX and XLSX are ZIPs: open with stdlib `zipfile`, require `word/document.xml` or `xl/workbook.xml`.
   - Reject macro-enabled content types and encrypted files.
   - Extension must match the detected type.
   - No new dependency needed.
4. Upload with `FileStorage.upload` (`src/modules/file/storage.py`) to private bucket **`operating-model`**, at `{tenant}/methodologies/{uuid}/{sanitized_filename}` (uuid keeps keys unique). Buckets created outside migrations, as `project-relay` was.
5. Call RPC `attach_client_methodology_document`: inserts the `client_methodology_documents` row and writes the uploaded event. Earlier rows stay as history; newest = current.
6. If the RPC fails, call `FileStorage.delete_many([path])`, log the orphan path if that fails too, return the error. Methodology keeps its previous document; client can retry against the same id.

## Error codes (p. 34)

| Error code | HTTP | When |
|---|---|---|
| `operating_model.methodology.file_missing` | 422 | No file or more than one |
| `operating_model.methodology.file_too_large` | 422 | Over the size limit |
| `operating_model.methodology.file_type_unsupported` | 422 | Not PDF, DOCX or XLSX by content |
| `operating_model.methodology.file_type_mismatch` | 422 | Extension doesn't match content |
| `operating_model.methodology.file_unreadable` | 422 | Corrupt, encrypted or macro-enabled |
| `operating_model.methodology.storage_failed` | 502 | Storage error; generic message, leaks no paths |

**Download:** `GET …/document` → 307 to a signed URL valid **10 minutes**, original filename in the download header.
