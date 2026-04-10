# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Lê Văn Tùng
**Nhóm:** Bàn Z - C401
**Ngày:** 10/4/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**

- Hai đoạn văn bản có high cosine similarity (độ tương đồng cosine cao) nghĩa là các vector biểu diễn (embedding) của chúng hướng về cùng một phía trong không gian vector. Về mặt ngữ nghĩa, điều này cho thấy hai đoạn văn bản đề cập đến những chủ đề hoặc ý tưởng giống nhau, ngay cả khi chúng không sử dụng chung chính xác các từ ngữ.

**Ví dụ HIGH similarity:**
* Sentence A: "Thời tiết hôm nay thực sự rất nóng."
* Sentence B: "Chiều nay ngoài trời oi bức đến mức cháy da."
* Tại sao tương đồng: Cả hai câu đều diễn đạt cùng một ý nghĩa về tình trạng nhiệt độ cao, dù sử dụng từ vựng khác nhau.

**Ví dụ LOW similarity:**
* Sentence A: "Tôi rất thích ăn mì cay."
* Sentence B: "Cơ học lượng tử là một nhánh của vật lý học."
* Tại sao khác: Hai câu này thuộc hai chủ đề hoàn toàn khác nhau (ẩm thực và khoa học), không có mối liên hệ ngữ nghĩa.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
* Khoảng cách Euclidean bị ảnh hưởng bởi độ dài (magnitude) của vector. osine similarity chỉ tập trung vào góc giữa các vector, giúp so sánh ý nghĩa mà không bị phụ thuộc vào độ dài của văn bản.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* 
- (document - overlap) / (chunk_size - overlap) 
> *Đáp án:* __23 chunks__

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*
- Số lượng chunks tăng lên (từ 23 lên 25).
---

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Recipes / Cooking (Sách nấu ăn lịch sử)

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain cooking/recipes vì tài liệu nấu ăn có cấu trúc rõ ràng (nguyên liệu, phương pháp, nhiệt độ, thời gian), tạo điều kiện tốt cho việc test retrieval với các query cụ thể có gold answer rõ ràng. Cuốn "The Boston Cooking-School Cook Book" (1910) từ Project Gutenberg có nội dung phong phú ~309,000 ký tự, bao gồm cả lý thuyết dinh dưỡng và phương pháp nấu ăn.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|------------------|
| 1 | recipe.md (The Boston Cooking-School Cook Book) | Project Gutenberg (https://www.gutenberg.org/) | 309,871 | doc_id, domain, author, doc_type, language, cuisine_scope, time_period, published_year, primary_topics, section_types, retrieval_tags |
| 2 | python_intro.txt | Lab sample (cung cấp bởi giảng viên) | 1,944 | source, extension |
| 3 | vector_store_notes.md | Lab sample (cung cấp bởi giảng viên) | ~2,000 | source, extension |
| 4 | rag_system_design.md | Lab sample (cung cấp bởi giảng viên) | 2,391 | source, extension |
| 5 | customer_support_playbook.txt | Lab sample (cung cấp bởi giảng viên) | 1,692 | source, extension |
| 6 | chunking_experiment_report.md | Lab sample (cung cấp bởi giảng viên) | ~2,000 | source, extension |
| 7 | vi_retrieval_notes.md | Lab sample (cung cấp bởi giảng viên) | ~2,000 | source, extension |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| heading_key | str | "food", "ways of cooking", "water (h_{2}o)" | Cho phép filter theo section cụ thể, tăng precision khi biết query thuộc chủ đề nào |
| section_type | str | "methods", "ingredient_reference", "preface" | Phân loại loại nội dung, giúp filter nhanh giữa lý thuyết và thực hành |
| domain | str | "recipes" | Phân biệt khi store chứa nhiều domain khác nhau |
| doc_id | str | "recipe_boston_cookbook_1910" | Quản lý document lifecycle (delete, update) |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên recipe.md + 2 tài liệu mẫu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| python_intro.txt (1944 chars) | FixedSizeChunker (`fixed_size`) | 13 | 195.7 | Thấp — cắt giữa câu |
| python_intro.txt | SentenceChunker (`by_sentences`) | 5 | 387.0 | Cao — giữ nguyên câu |
| python_intro.txt | RecursiveChunker (`recursive`) | 14 | 136.9 | Trung bình — tách theo cấu trúc |
| rag_system_design.md (2391 chars) | FixedSizeChunker (`fixed_size`) | 16 | 196.3 | Thấp |
| rag_system_design.md | SentenceChunker (`by_sentences`) | 5 | 476.0 | Cao |
| rag_system_design.md | RecursiveChunker (`recursive`) | 20 | 117.7 | Trung bình |
| customer_support_playbook.txt (1692 chars) | FixedSizeChunker (`fixed_size`) | 11 | 199.3 | Thấp |
| customer_support_playbook.txt | SentenceChunker (`by_sentences`) | 4 | 421.0 | Cao |
| customer_support_playbook.txt | RecursiveChunker (`recursive`) | 14 | 119.1 | Trung bình |
| recipe.md (309,238 chars) | FixedSizeChunker (`fixed_size`) | 688 | 499.4 | Thấp — cắt giữa đoạn, mất context |
| recipe.md | SentenceChunker (`by_sentences`) | 741 | 401.2 | Trung bình — giữ câu nhưng chunk lớn |
| recipe.md | RecursiveChunker (`recursive`) | 857 | 359.0 | Cao — tách theo paragraph rồi câu |

### Strategy Của Tôi

**Loại:** RecursiveChunker(chunk_size=500) + Section-based pre-splitting + Metadata enrichment

**Mô tả cách hoạt động:**
> Strategy gồm 2 tầng: (1) Pre-split tài liệu theo heading markdown (## / ###) để tách ra từng section (Food, Water, Milk, Ways of Cooking...). (2) Áp dụng RecursiveChunker(chunk_size=500) trên từng section, gắn metadata (heading_key, section_type, domain) vào mỗi chunk. Separator priority: `\n\n` → `\n` → `". "` → `" "` → `""`. Chỉ index các section target (food, water, milk, ways of cooking) thay vì toàn bộ sách.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Cuốn sách nấu ăn có cấu trúc heading rõ ràng theo chương/section. Section-based splitting giúp mỗi chunk thuộc đúng một chủ đề, và metadata heading_key cho phép filter chính xác (e.g., chỉ tìm trong "ways of cooking"). RecursiveChunker giữ paragraph trọn vẹn — quan trọng vì mỗi paragraph trong sách thường mô tả một khái niệm/phương pháp hoàn chỉnh.

**Code snippet:**
```python
def build_chunked_documents(text: str) -> list[Document]:
    chunker = RecursiveChunker(chunk_size=500)
    sections = split_sections(text)  # split by ## / ###
    docs = []
    for heading, section_text in sections:
        heading_key = normalize_heading(heading)
        if heading_key not in TARGET_HEADING_KEYS:
            continue
        section_type = infer_section_type(heading)
        chunks = chunker.chunk(section_text)
        for chunk in chunks:
            docs.append(Document(
                id=f"recipe_chunk_{idx:04d}",
                content=chunk,
                metadata={"heading_key": heading_key, "section_type": section_type, ...}
            ))
    return docs
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|---------|
| recipe.md (full) | RecursiveChunker baseline | 857 | 359.0 | Thấp — quá nhiều chunks, noise cao |
| recipe.md (target sections) | **Section + RecursiveChunker (của tôi)** | 39 | ~350 | Cao — ít chunks, đúng chủ đề, có metadata filter |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Đinh Thái Tuấn | Section-based + RecursiveChunker(500) + metadata filter | 6/10 | Filter theo heading_key giúp Q1, Q5 chính xác | Mock embedder hạn chế semantic matching |
| Nguyễn Đức Sĩ | FixedSizeChunker(500, overlap=100) | 4/10 | Đơn giản, dễ implement | Cắt giữa paragraph, mất context |
| Lê Văn Tùng (tôi)| RecursiveChunker(300) | 5/10 | Giữ nguyên câu trọn vẹn | không có metadata filter |
| Lê Thanh Thưởng | RecursiveChunker(300) + metadata | 5/10 | Chunk nhỏ, nhiều granularity | Chunk quá nhỏ đôi khi mất context |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Section-based + RecursiveChunker cho kết quả tốt nhất trên domain cookbook vì tận dụng cấu trúc heading sẵn có của Markdown. Metadata filter (heading_key) giúp thu hẹp vùng tìm kiếm đáng kể — thay vì search 857 chunks, chỉ cần search 5-10 chunks trong đúng section. Tuy nhiên, với real embedder (OpenAI), gap giữa các strategy sẽ nhỏ hơn vì semantic search bù đắp cho chunking kém.

---

## 4. My Approach — Cá nhân (10 điểm)
### Chunking Functions

**`RecursiveChunker.chunk` / `_split`** — approach:
>Tôi triển khai thuật toán đệ quy mô phỏng cấu trúc phân cấp của văn bản (Paragraph -> Sentence -> Word). Nếu một đoạn văn vượt quá chunk_size, hệ thống sẽ ưu tiên tách tại các điểm ngắt tự nhiên (\n\n, \n, . ). Điều này đảm bảo tính "độc lập về độ dài" mà tôi đã đề cập ở phần 1.1; bằng cách giữ các đoạn có độ dài ổn định và ngữ cảnh hội tụ, việc tính Cosine Similarity sau này sẽ đạt độ chính xác cao hơn.

### EmbeddingStore
**`add_documents` + `search`**:
> Trong phương thức search, tôi sử dụng Dot Product để tính toán độ tương đồng giữa query và văn bản. Vì các vector từ mock embedder đã được chuẩn hóa (Unit Vector), nên về mặt toán học, Dot Product lúc này chính là Cosine Similarity mà tôi đã phân tích ở phần Warm-up. Kết quả được sắp xếp giảm dần để trả về những đoạn văn có "hướng" gần nhất với câu hỏi.

**`search_with_filter` + `delete_document`**:
> Để tối ưu hóa hiệu suất, tôi áp dụng cơ chế Pre-filtering. Hệ thống sẽ lọc các metadata (như heading_key hay section_type) trước khi thực hiện tính toán vector. Điều này giúp loại bỏ các "nhiễu" từ các chủ đề không liên quan (ví dụ: loại bỏ "Cơ học lượng tử" khi đang tìm về "Mì cay" như ví dụ ở Ex 1.1), giúp không gian tìm kiếm sạch hơn và kết quả chính xác hơn.

###KnowledgeBaseAgent
> **answer** Tôi thiết kế quy trình RAG theo 3 giai đoạn: Truy xuất (Retrieval) -> Làm giàu ngữ cảnh (Augmentation) -> Sinh phản hồi (Generation). Prompt được cấu trúc chặt chẽ để LLM chỉ tập trung vào các chunk có độ tương đồng cao nhất đã tìm được, hạn chế tình trạng "hallucination" khi các vector không thực sự liên quan nhưng vẫn bị đưa vào ngữ cảnh.
### Test Results

```
============================= test session starts =============================
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED
============================= 42 passed in 2.23s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

> **Lưu ý:** Kết quả dùng `_mock_embed` (hash-based, không phải semantic embedding thực). Với embedder thực (e.g., all-MiniLM-L6-v2), kết quả sẽ phản ánh ngữ nghĩa chính xác hơn.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a programming language | Java is a programming language | high | 0.1135 | Không — mock embedder không capture semantic |
| 2 | The weather is sunny today | Machine learning uses neural networks | low | 0.0809 | Đúng — score thấp, hai domain khác nhau |
| 3 | Vector databases store embeddings | Embeddings are stored in vector stores | high | 0.1632 | Không — same meaning nhưng mock score thấp |
| 4 | I love eating pizza | Pizza is my favorite food | high | -0.1968 | Không — mock cho score âm dù nghĩa giống |
| 5 | The cat sat on the mat | Financial markets crashed yesterday | low | 0.0263 | Đúng — score gần 0, không liên quan |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả thực tế cho thấy sự khác biệt khổng lồ giữa "ngữ nghĩa" và "đại diện số". Như tôi đã nêu ở phần 1.1, Cosine Similarity chỉ thực sự mạnh mẽ khi vector embedding phản ánh đúng bản chất nội dung. Mock embedder trong bài Lab này mới chỉ xử lý ở mức độ phân tách dữ liệu, chưa đạt tới mức độ "hiểu" để thấy được sự tương đồng giữa "nóng" và "oi bức".

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer | Chunk nào chứa thông tin? |
|---|-------|-------------|---------------------------|
| 1 | What are the principal ways of cooking listed in the book? | Boiling, broiling, stewing, roasting, baking, frying, sautéing, braising, and fricasseeing | Section "Ways of Cooking" |
| 2 | At what temperatures does water boil and simmer? | Water boils at 212°F and simmers at around 185°F | Section "Water (H₂O)" |
| 3 | Why does milk sour according to the text? | A germ converts lactose to lactic acid, precipitating casein into curd and whey | Section "Milk" |
| 4 | How is fat tested for frying temperature? | Drop a one-inch cube of bread; if golden brown in forty seconds, fat is ready | Section "Ways of Cooking" |
| 5 | What is the chief office of proteids? | Proteids chiefly build and repair tissues, and can also furnish energy | Section "Food" |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Principal ways of cooking? | "The principal ways of cooking are boiling, broiling, stewing..." (filtered: ways of cooking) | 0.3184 | Có ✓ | Boiling, broiling, stewing, roasting, baking, frying, sautéing, braising, fricasseeing |
| 2 | Water boil/simmer temperatures? | "Water freezes at 32°F., boils at 212°F..." (filtered: water) | 0.0690 | Có ✓ | Đúng chunk nhưng agent answer thiếu chi tiết (extractive LLM hạn chế) |
| 3 | Why does milk sour? | "scalded milk, temperature of 196°F..." (no filter match) | 0.2309 | Không ✗ | Retrieval sai chunk — chunk về scalded milk thay vì souring process |
| 4 | Fat frying temperature test? | "Principal ways of cooking..." (filtered: ways of cooking) | 0.2116 | Một phần | Chunk chứa info về frying nhưng không đúng đoạn test fat |
| 5 | Chief office of proteids? | "The chief office of proteids is to build and repair tissues..." (filtered: food) | 0.1664 | Có ✓ | Agent trả sai (extractive LLM lấy câu không liên quan) |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

> **Phân tích:** Tỉ lệ thành công đạt 3/5. Việc sử dụng Cosine Similarity (thông qua Dot Product trên vector chuẩn hóa) kết hợp với Metadata Filtering đã chứng minh được hiệu quả. Dù Mock Embedder còn hạn chế, nhưng chiến lược Section-based splitting (chia theo tiêu đề) giúp đảm bảo các chunk không bị quá dài, từ đó tránh được sai số về Magnitude mà tôi đã cảnh báo ở phần 1.1

---

## 7. What I Learned (5 điểm — Demo)

* Điều học được từ thành viên khác:

 	* Overlap là "vùng đệm": Từ Nguyễn Đức Sĩ, tôi thấy overlap giúp giữ vững "hướng" của vector tại ranh giới chunk, tránh mất ngữ cảnh.

	* Độ phân giải (Granularity): Từ Lê Thanh Thưởng, chunk nhỏ giúp tìm chi tiết tốt nhưng dễ gây "nhiễu" vì thiếu thông tin bao quát.

* Điều học được từ nhóm khác:

	* Cấu trúc quyết định hiệu quả: Các nhóm dùng FAQ/SOP có kết quả tốt hơn vì query và chunk dễ đạt high cosine similarity hơn dạng văn xuôi (prose) của nhóm mình.

* Phân tích thất bại (Failure Case):

	* Lỗi ngữ nghĩa: Query 3 ("Milk souring") sai vì mock embedder dựa trên hash ký tự. Nó thấy từ "milk" chung nhưng không phân biệt 	được "chua" và "đun nóng", dẫn đến lệch hướng vector.

* Hướng cải thiện:

	* Semantic Embedding: Thay mock bằng OpenAI embedding để thực sự bắt được ý nghĩa văn bản.

	* Hybrid Search: Kết hợp vector với keyword search để xử lý chính xác các thuật ngữ đặc thù (nhiệt độ, thành phần).

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 9 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 9 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **95 / 100** |
