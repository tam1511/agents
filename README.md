# agents

# 🤖 AI Trends Content Curator Agents

## 📝 Mô tả dự án

**AI Trends Content Curator Agents** là hệ thống tạo nội dung tự động sử dụng AI để theo dõi, phân tích và tạo nội dung về các xu hướng công nghệ AI mới nhất. 

## Tính năng chính

- **Theo dõi xu hướng AI:** Tự động thu thập và phân tích dữ liệu xu hướng từ Reddit, Twitter, HackerNews, YouTube
- **Chấm điểm xu hướng:** Đánh giá mức độ hot trend của các chủ đề AI theo thời gian thực
- **Chiến lược nội dung thông minh:** Quyết định tạo, bỏ qua, hoặc quảng bá nội dung dựa trên điểm xu hướng
- **Đa nền tảng:** Tạo nội dung cho Blog, Twitter, LinkedIn, Newsletter với định dạng tối ưu cho từng nền tảng
- **Theo dõi hiệu suất:** Thống kê engagement, độ phủ chủ đề, và hiệu suất theo nền tảng
- **Đội ngũ curator chuyên biệt:** Nhiều AI agent với chuyên môn khác nhau (AI Research, Tools, Business, Ethics)

## 🛠️ Quy trình hoạt động

1. **Nghiên cứu xu hướng** → Tìm kiếm tin tức, chủ đề AI hot
2. **Tính điểm xu hướng** → Đánh giá tiềm năng engagement từ nhiều nguồn
3. **Đánh giá chiến lược** → Quyết định CREATE/SKIP/PROMOTE dựa trên strategy
4. **Tạo & đăng nội dung** → Xuất bản lên các nền tảng phù hợp
5. **Cập nhật metrics** → Theo dõi engagement và hiệu suất
6. **Phân tích & tối ưu** → Cải thiện strategy dựa trên kết quả

## 🏗️ Kiến trúc hệ thống

```
📁 Dự án
├── trends.py              # Thu thập dữ liệu xu hướng
├── profiles.py    # Quản lý tài khoản & metrics
├── curator.py           # AI agents chính
├── curator_templates.py  # Hướng dẫn & prompts
├── mcp_servers.py # Cấu hình MCP servers
├── 🖥app.py       # Script chạy chính
└── [MCP Servers]         # Các microservices hỗ trợ
```
### 📚 Resources

- **YouTube**  
  Sorry, I can’t remember how many videos I watched!!

- **Courses**  
  *The Complete Agentic AI Engineering Course* – by a Data Scientist (which made it very approachable for me as someone in DS/Engineering).  
  👉 Highly recommended: [Udemy Course](https://www.udemy.com/course/the-complete-agentic-ai-engineering-course/?couponCode=KEEPLEARNING)

- **Articles & References**
  - [MCP Introduction – Hugging Face Blog](https://huggingface.co/blog/Kseniase/mcp)
  - [MCP Marketplace – mcp.so](https://mcp.so)
  - [MCP Marketplace – Glama.ai](https://glama.ai/mcp)
  - [Top 11 Essential MCP Libraries – Hugging Face Blog](https://huggingface.co/blog/LLMhacker/top-11-essential-mcp-libraries)
  - [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
