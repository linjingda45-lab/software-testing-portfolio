-- 电商订单系统初始化脚本（MySQL 8.0）
-- 执行方式：mysql --no-defaults -h127.0.0.1 -P3307 -uroot ecommerce_test < sql/init.sql

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录名',
    password VARCHAR(100) NOT NULL COMMENT '演示项目使用明文，生产环境应加密存储',
    nickname VARCHAR(50) NOT NULL DEFAULT '' COMMENT '昵称',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1-正常 0-禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '商品名称',
    price DECIMAL(10, 2) NOT NULL COMMENT '单价',
    stock INT NOT NULL DEFAULT 0 COMMENT '库存',
    category VARCHAR(50) NOT NULL DEFAULT '' COMMENT '分类',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1-在售 0-下架',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
    user_id BIGINT NOT NULL COMMENT '下单用户',
    product_id BIGINT NOT NULL COMMENT '商品ID',
    quantity INT NOT NULL COMMENT '购买数量',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    status VARCHAR(20) NOT NULL DEFAULT 'CREATED' COMMENT 'CREATED/PAID/SHIPPED/COMPLETED/CANCELLED',
    request_id VARCHAR(64) NOT NULL COMMENT '幂等请求号，防重复提交',
    address VARCHAR(200) NOT NULL COMMENT '收货地址',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_request (user_id, request_id),
    KEY idx_user_status (user_id, status),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_orders_product FOREIGN KEY (product_id) REFERENCES products (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

INSERT INTO users (id, username, password, nickname, status) VALUES
(1, 'testuser', '123456', '测试用户', 1),
(2, 'otheruser', '123456', '其他用户', 1);

INSERT INTO products (id, name, price, stock, category, status) VALUES
(1, '机械键盘', 299.00, 50, '数码配件', 1),
(2, '无线鼠标', 99.00, 100, '数码配件', 1),
(3, '27寸显示器', 899.00, 20, '显示设备', 1),
(4, '降噪耳机', 199.00, 0, '音频设备', 1),
(5, '下架商品', 59.00, 10, '其他', 0);

-- 重置自增起点，保证商品/用户 ID 与测试数据一致
ALTER TABLE users AUTO_INCREMENT = 3;
ALTER TABLE products AUTO_INCREMENT = 6;
ALTER TABLE orders AUTO_INCREMENT = 1;
