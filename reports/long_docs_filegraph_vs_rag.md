# FileGraphDB vs Advanced RAG Baseline

Folder: `C:\Users\user\Desktop\file based graph proj\samples\long_docs`
Query: `what caused the beta release delay`
Limit: `5`

## Build Summary

- FileGraphDB documents/chunks: `14`
- FileGraphDB edges: `45`
- Advanced RAG chunks: `22`

## Token Summary

| Method | Total tokens | Selected tokens | Saved tokens | Saved percent |
|---|---:|---:|---:|---:|
| FileGraphDB | 14217 | 5725 | 8492 | 59.73% |
| Advanced RAG | 17139 | 2750 | 14389 | 83.95% |

## FileGraphDB Results

- `delay_report.txt` score=0.754 reason=query semantic/keyword match
- `huge_report.txt#chunk-0011` score=0.521 reason=query semantic/keyword match
- `huge_report.txt#chunk-0001` score=0.512 reason=query semantic/keyword match
- `huge_report.txt#chunk-0010` score=0.507 reason=query semantic/keyword match
- `huge_report.txt#chunk-0008` score=0.503 reason=query semantic/keyword match

## Advanced RAG Results

- `huge_report.txt#chunk-0020` score=0.075 semantic=0.000 keyword=0.000 rerank=0.750
- `huge_report.txt#chunk-0001` score=0.075 semantic=0.000 keyword=0.000 rerank=0.750
- `huge_report.txt#chunk-0002` score=0.075 semantic=0.000 keyword=0.000 rerank=0.750
- `huge_report.txt#chunk-0003` score=0.075 semantic=0.000 keyword=0.000 rerank=0.750
- `huge_report.txt#chunk-0004` score=0.075 semantic=0.000 keyword=0.000 rerank=0.750

## Overlap

- `huge_report.txt`