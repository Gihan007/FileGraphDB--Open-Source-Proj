# `text_features.py` Visual Explanation

This diagram explains how `filegraphdb/text_features.py` turns text files into numbers and features that FileGraphDB can compare.

## 0. One Full Detailed Diagram

```mermaid
flowchart TD
    %% Inputs
    A["Input: list of Document objects<br/>Document.id<br/>Document.rel_path<br/>Document.text"]
    B["List comprehension<br/>doc.text for every document"]

    %% Vectorizer construction
    C["TfidfVectorizer settings<br/>lowercase=True<br/>stop_words=english<br/>ngram_range=(1,2)<br/>min_df=1<br/>max_df=0.95<br/>sublinear_tf=True"]
    D["fit_transform(texts)<br/>FIT: learn vocabulary + IDF statistics<br/>TRANSFORM: convert docs to TF-IDF numbers"]
    DFail{"ValueError?<br/>Example: all words removed"}
    D2["Fallback TfidfVectorizer<br/>stop_words=None"]
    E["Output: self.tfidf<br/>Sparse matrix<br/>rows = documents<br/>columns = learned terms<br/>values = term importance"]

    %% Feature names
    F["get_feature_names_out"]
    G["self.feature_names<br/>NumPy array of vocabulary terms<br/>Example: brady bill, waiting period"]

    %% Semantic vector branch
    H["_build_semantic_vectors"]
    I{"prefer_sentence_transformers?"}
    J["Try import SentenceTransformer"]
    K["Load embedding model<br/>default: all-MiniLM-L6-v2"]
    L["Encode every document text<br/>normalize_embeddings=True"]
    M["self.embeddings<br/>Semantic vectors from model"]
    N["If model unavailable/fails<br/>self._st_model=None"]

    %% LSA fallback branch
    O["_build_lsa_vectors"]
    P["Read TF-IDF shape<br/>rows=docs, cols=terms"]
    Q["Choose SVD dimensions<br/>max_components = min 128, rows-1, cols-1"]
    R{"Enough docs and terms?<br/>max_components >= 2"}
    S["Use raw TF-IDF dense matrix<br/>normalize rows"]
    T["TruncatedSVD<br/>reduce TF-IDF into semantic space"]
    U["normalize reduced vectors"]
    V["self.embeddings<br/>Semantic-ish LSA vectors"]

    %% Attach features
    W["_attach_extracted_features"]
    X["Loop through each document"]
    Y["_top_terms(index, limit=12)"]
    Y1["Get one TF-IDF row<br/>self.tfidf.getrow(index)"]
    Y2{"Any non-zero terms?"}
    Y3["Sort row scores descending<br/>np.argsort(row.data)"]
    Y4["Map term indexes to words<br/>self.feature_names at row indexes"]
    Z["keywords tuple<br/>top important terms"]
    AA["extract_entities(doc.text)"]
    AB["Regex extract:<br/>capitalized phrases<br/>dates<br/>emails<br/>URLs"]
    AC["Filter stopwords<br/>limit to useful entities"]
    AD["entities tuple"]
    AE["topics tuple<br/>first 6 keywords"]
    AF["replace(doc, keywords, topics, entities)"]
    AG["self.documents<br/>enriched Document objects"]
    AH["self.id_to_index<br/>doc.id -> row index"]

    %% Similarity methods
    AI["semantic_similarity_matrix"]
    AJ["cosine_similarity(self.embeddings)"]
    AK["Semantic similarity matrix<br/>doc-vs-doc meaning similarity"]

    AL["keyword_similarity_matrix"]
    AM["cosine_similarity(self.tfidf)"]
    AN["Keyword similarity matrix<br/>doc-vs-doc TF-IDF similarity"]

    %% Query scoring
    AO["query_scores(query)"]
    AP["Transform query with same vectorizer<br/>query_tfidf"]
    AQ["Keyword query scores<br/>cosine_similarity(query_tfidf, self.tfidf)"]
    AR{"self._st_model exists?"}
    AS["SentenceTransformer encode query"]
    AT["_lsa_query_vector(query_tfidf)"]
    AU{"self._svd exists?"}
    AV["Transform query through SVD<br/>normalize"]
    AW["Fallback query TF-IDF dense<br/>normalize"]
    AX["Semantic query scores<br/>cosine_similarity(query_embedding, self.embeddings)"]
    AY["Return:<br/>semantic_scores, keyword_scores"]

    %% Helper functions
    BA["jaccard(left, right)<br/>shared items / all unique items"]
    BB["direct_reference_score(source,target)<br/>path mention = 1.0<br/>filename mention = 0.9<br/>stem mention = 0.65"]
    BC["confidence_from_score(score)<br/>sigmoid confidence curve"]

    %% Core outputs
    CA["core.py uses outputs"]
    CB["Build relationship edges<br/>semantic_score<br/>keyword_score<br/>entity_overlap<br/>topic_overlap<br/>direct_ref"]
    CC["Retrieve query results<br/>semantic_scores + keyword_scores"]

    %% Connections
    A --> B
    B --> C
    C --> D
    D --> DFail
    DFail -- no --> E
    DFail -- yes --> D2
    D2 --> E

    E --> F
    F --> G

    E --> H
    B --> H
    H --> I
    I -- yes --> J
    J --> K
    K --> L
    L --> M
    J -. exception .-> N
    I -- no --> O
    N --> O
    E --> O
    O --> P
    P --> Q
    Q --> R
    R -- no --> S
    S --> V
    R -- yes --> T
    T --> U
    U --> V
    M --> AI
    V --> AI

    A --> W
    E --> W
    G --> W
    W --> X
    X --> Y
    Y --> Y1
    Y1 --> Y2
    Y2 -- no --> Z
    Y2 -- yes --> Y3
    Y3 --> Y4
    Y4 --> Z
    X --> AA
    AA --> AB
    AB --> AC
    AC --> AD
    Z --> AE
    Z --> AF
    AD --> AF
    AE --> AF
    AF --> AG
    AG --> AH

    AI --> AJ
    AJ --> AK
    E --> AL
    AL --> AM
    AM --> AN

    AO --> AP
    AP --> AQ
    AO --> AR
    AR -- yes --> AS
    AR -- no --> AT
    AT --> AU
    AU -- yes --> AV
    AU -- no --> AW
    AS --> AX
    AV --> AX
    AW --> AX
    AQ --> AY
    AX --> AY

    AK --> CA
    AN --> CA
    AG --> CA
    AH --> CA
    BA --> CB
    BB --> CB
    BC --> CB
    CA --> CB
    AY --> CC
    CA --> CC

    %% Styling
    classDef input fill:#e8f3ff,stroke:#2b6cb0,color:#102a43;
    classDef process fill:#f7fafc,stroke:#4a5568,color:#1a202c;
    classDef output fill:#e6fffa,stroke:#2c7a7b,color:#123;
    classDef decision fill:#fff5d6,stroke:#b7791f,color:#3b2f00;
    classDef core fill:#f0fff4,stroke:#2f855a,color:#123;

    class A,B input;
    class C,D,D2,F,H,J,K,L,O,P,Q,S,T,U,W,X,Y,Y1,Y3,Y4,AA,AB,AC,AI,AJ,AL,AM,AO,AP,AQ,AS,AT,AV,AW,AX,BA,BB,BC process;
    class E,G,M,V,Z,AD,AE,AF,AG,AH,AK,AN,AY output;
    class DFail,I,R,Y2,AR,AU decision;
    class CA,CB,CC core;
```

## 1. Big Picture

```mermaid
flowchart TD
    Docs[Raw Document objects<br/>doc.text, doc.id, doc.path]
    Texts[List of document texts<br/>doc.text for each doc]
    TFIDF[TfidfVectorizer.fit_transform<br/>learn vocabulary + create TF-IDF matrix]
    Names[get_feature_names_out<br/>vocabulary words/phrases]
    Semantic[_build_semantic_vectors<br/>sentence-transformers OR LSA]
    Attach[_attach_extracted_features<br/>keywords + topics + entities]
    Lookup[id_to_index<br/>document id -> matrix row]

    Docs --> Texts
    Texts --> TFIDF
    TFIDF --> Names
    TFIDF --> Semantic
    Docs --> Attach
    TFIDF --> Attach
    Names --> Attach
    Attach --> Lookup

    TFIDF --> KeywordSim[keyword_similarity_matrix]
    Semantic --> SemanticSim[semantic_similarity_matrix]
    Lookup --> Core[core.py relationship builder]
    KeywordSim --> Core
    SemanticSim --> Core
    Attach --> Core
```

In simple words:

```text
documents
  -> important word matrix
  -> meaning vectors
  -> keywords/topics/entities
  -> similarity scores
  -> graph edges
```

## 2. Example Input

Imagine three files:

```text
doc1: "The Brady Bill requires a waiting period."
doc2: "Background checks are part of gun legislation."
doc3: "Tomatoes need soil and water."
```

They arrive as `Document` objects:

```mermaid
flowchart LR
    D1[Document doc1<br/>text: Brady Bill waiting period]
    D2[Document doc2<br/>text: Background checks gun legislation]
    D3[Document doc3<br/>text: Tomatoes soil water]
```

## 3. TF-IDF Matrix

This line:

```python
self.tfidf = self.vectorizer.fit_transform([doc.text for doc in documents])
```

does this:

```mermaid
flowchart TD
    Raw[Raw texts]
    Fit[fit<br/>learn vocabulary]
    Transform[transform<br/>turn each document into numbers]
    Matrix[TF-IDF matrix<br/>rows=docs, columns=terms]

    Raw --> Fit
    Fit --> Transform
    Transform --> Matrix
```

Example matrix:

```text
                  brady bill   waiting period   background check   gun legislation   tomatoes   soil
doc1                  high          high              0                 0              0        0
doc2                   0             0               high              high            0        0
doc3                   0             0                0                 0             high     high
```

Purpose:

```text
Find documents that share important words or phrases.
```

## 4. Feature Names

This line:

```python
self.feature_names = np.asarray(self.vectorizer.get_feature_names_out())
```

creates the column labels for the TF-IDF matrix.

```mermaid
flowchart LR
    Matrix[TF-IDF matrix columns]
    Names[feature_names array]

    Matrix --> Names

    Names --> N1[brady bill]
    Names --> N2[waiting period]
    Names --> N3[background check]
    Names --> N4[gun legislation]
    Names --> N5[tomatoes]
```

Purpose:

```text
When a document has high TF-IDF score in column 10,
feature_names tells us what word/phrase column 10 means.
```

## 5. Semantic Embeddings

This line:

```python
self.embeddings = self._build_semantic_vectors(prefer_sentence_transformers)
```

creates one meaning vector per document.

```mermaid
flowchart TD
    Docs[Documents]
    Choice{Use sentence-transformers?}
    ST[Open-source embedding model<br/>all-MiniLM-L6-v2]
    LSA[Fallback local semantic vectors<br/>TF-IDF + TruncatedSVD]
    Emb[Embeddings matrix<br/>one meaning vector per doc]

    Docs --> Choice
    Choice -- yes --> ST
    Choice -- no or model fails --> LSA
    ST --> Emb
    LSA --> Emb
```

Example:

```text
doc1 embedding -> [politics, guns, law]
doc2 embedding -> [politics, guns, law]
doc3 embedding -> [gardening, plants, soil]
```

Purpose:

```text
Find documents with similar meaning, even if exact words are different.
```

## 6. Attach Extracted Features

This line:

```python
self.documents = self._attach_extracted_features()
```

adds sticky-note style features to each document.

```mermaid
flowchart TD
    Doc[Document]
    TopTerms[_top_terms<br/>from TF-IDF]
    Entities[extract_entities<br/>capitalized names, dates, emails, URLs]
    Topics[topics = first 6 keywords]
    NewDoc[Updated Document<br/>keywords + topics + entities]

    Doc --> TopTerms
    Doc --> Entities
    TopTerms --> Topics
    TopTerms --> NewDoc
    Entities --> NewDoc
    Topics --> NewDoc
```

Example:

```text
Before:
Document(text="The Brady Bill requires a waiting period.", keywords=(), topics=(), entities=())

After:
Document(
  keywords=("brady bill", "waiting period"),
  topics=("brady bill", "waiting period"),
  entities=("Brady Bill",)
)
```

Purpose:

```text
core.py can later create graph edges from shared keywords, topics, and entities.
```

## 7. ID To Index Lookup

This line:

```python
self.id_to_index = {doc.id: index for index, doc in enumerate(self.documents)}
```

creates a map from document ID to row number.

```mermaid
flowchart LR
    ID1[doc1 id: abc123] --> Row0[row 0 in TF-IDF/embedding matrix]
    ID2[doc2 id: def456] --> Row1[row 1 in TF-IDF/embedding matrix]
    ID3[doc3 id: ghi789] --> Row2[row 2 in TF-IDF/embedding matrix]
```

Purpose:

```text
Documents have IDs.
Matrices have row numbers.
This dictionary connects them.
```

## 8. Similarity Matrices

These methods:

```python
semantic_similarity_matrix()
keyword_similarity_matrix()
```

compare every document with every other document.

```mermaid
flowchart TD
    TFIDF[TF-IDF matrix]
    Emb[Embeddings matrix]
    Cos1[cosine_similarity]
    Cos2[cosine_similarity]
    Keyword[Keyword similarity matrix]
    Semantic[Semantic similarity matrix]

    TFIDF --> Cos1 --> Keyword
    Emb --> Cos2 --> Semantic
```

Example output:

```text
Keyword similarity:
        doc1   doc2   doc3
doc1    1.00   0.21   0.00
doc2    0.21   1.00   0.00
doc3    0.00   0.00   1.00

Semantic similarity:
        doc1   doc2   doc3
doc1    1.00   0.78   0.05
doc2    0.78   1.00   0.04
doc3    0.05   0.04   1.00
```

Purpose:

```text
core.py uses these scores to decide whether two files should be connected.
```

## 9. Query Scores

When user asks:

```text
"background check waiting period"
```

`query_scores()` does this:

```mermaid
flowchart TD
    Query[User query]
    QueryTFIDF[Convert query to TF-IDF vector]
    KeywordCompare[Compare query TF-IDF vs document TF-IDF]
    QuerySemantic[Convert query to semantic vector]
    SemanticCompare[Compare query semantic vector vs document embeddings]
    Scores[Return semantic_scores + keyword_scores]

    Query --> QueryTFIDF
    QueryTFIDF --> KeywordCompare
    Query --> QuerySemantic
    QuerySemantic --> SemanticCompare
    KeywordCompare --> Scores
    SemanticCompare --> Scores
```

Purpose:

```text
Find which documents are most relevant to the user query.
```

## 10. Whole Data Flow In One View

```mermaid
flowchart TD
    A[Raw files]
    B[Document objects]
    C[Document texts]
    D[TF-IDF matrix]
    E[Feature names]
    F[Semantic embeddings]
    G[Keywords]
    H[Topics]
    I[Entities]
    J[Enriched Documents]
    K[Similarity matrices]
    L[core.py graph builder]
    M[Edges in SQLite]

    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    G --> H
    B --> I
    G --> J
    H --> J
    I --> J
    F --> K
    D --> K
    J --> L
    K --> L
    L --> M
```
