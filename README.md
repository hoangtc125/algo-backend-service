# Đồ án tốt nghiệp

Hệ thống quản lý thông tin Câu lạc bộ và áp dụng phân cụm vào bài toán tuyển thành viên

## Mô tả

Dự án này là đồ án tốt nghiệp của tôi, Trần Công Hoàng.
Đây là server được dựng bằng FastAPI

## Cài đặt

1. Clone repo này về máy của bạn:

```shell
git clone https://github.com/hoangtc125/algo-backend-service
```

2. Di chuyển vào thư mục dự án:

```shell
cd [Tên thư mục dự án]
```

3. Cài đặt các yêu cầu:

```shell
pip install -r requirements.txt
```

4. Thiết lập các biến môi trường bằng cách tạo một tệp .env và điền các giá trị cấu hình

## Cấu trúc thư mục

### Docker

Dự án này sử dụng Docker để triển khai và quản lý các dịch vụ phụ sau:

- MongoDB: Cơ sở dữ liệu NoSQL được sử dụng cho ứng dụng.

- RabbitMQ: Hệ thống message broker để xử lý các message và event trong ứng dụng.

- Prometheus: Hệ thống giám sát và thu thập dữ liệu về hiệu suất ứng dụng.

- Grafana: Công cụ trực quan hóa dữ liệu và xây dựng bảng điều khiển cho dữ liệu giám sát từ Prometheus.

Cấu trúc thư mục Docker của dự án:

```shell
docker
├── mongodb.compose.yml
├── rabbitmq.compose.yml
├── prometheus
│   └── prometheus.yml
├── grafana
│   └── provisioning
└── monitor.compose.yml
```

Bạn có thể sử dụng Docker Compose để triển khai các dịch vụ Docker này. Hãy thực hiện các bước sau:

```shell
docker compose -f docker/mongodb.compose.yml up -d 
docker compose -f docker/rabbitmq.compose.yml up -d
docker compose -f docker/monitor.compose.yml up -d
```

Lưu ý: Đảm bảo rằng Docker đã được cài đặt và đang chạy trên máy tính của bạn.

### Tài nguyên

Thư mục resources chứa các tài nguyên hữu ích cho dự án:

```shell
resources
├── grafana.json
├── algo-firebase.json
└── response_code.json
```

- grafana.json: Tệp cấu hình JSON cho bảng điều khiển Grafana.
- algo-firebase.json: Tệp cấu hình JSON cho Firebase, nếu có.
- response_code.json: Tệp chứa mã phản hồi HTTP chuẩn và thông báo tương ứng.

### Log

Thư mục log chứa các tệp log của ứng dụng.

### Requirements.txt

Tệp requirements.txt chứa danh sách các gói phụ thuộc Python và phiên bản tương ứng.

### .pre-commit-config.yaml

Tệp .pre-commit-config.yaml chứa cấu hình cho pre-commit hooks để kiểm tra mã nguồn trước khi commit.
