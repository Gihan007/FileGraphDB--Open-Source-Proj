# FileGraphDB vs Advanced RAG Baseline

Folder: `C:\Users\user\Desktop\file based graph proj\samples\text_notes`
Query: `what caused the project delay`
Limit: `3`

## Build Summary

- FileGraphDB documents/chunks: `5`
- FileGraphDB edges: `2`
- Advanced RAG chunks: `5`

## Token Summary

| Method | Total tokens | Selected tokens | Saved tokens | Saved percent |
|---|---:|---:|---:|---:|
| FileGraphDB | 194 | 125 | 69 | 35.57% |
| Advanced RAG | 192 | 115 | 77 | 40.1% |

## FileGraphDB Results

- `vendor_delay.txt` score=0.693 reason=query semantic/keyword match
- `project_timeline.txt` score=0.648 reason=query semantic/keyword match
- `report_summary.txt` score=0.430 reason=query semantic/keyword match

## Advanced RAG Results

- `vendor_delay.txt#chunk-0001` score=0.683 semantic=0.896 keyword=0.220 rerank=0.667
- `project_timeline.txt#chunk-0001` score=0.641 semantic=0.892 keyword=0.077 rerank=0.667
- `garden_plan.txt#chunk-0001` score=0.288 semantic=0.374 keyword=0.084 rerank=0.333

## Overlap

- `project_timeline.txt`
- `vendor_delay.txt`