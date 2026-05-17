import random
import csv
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path


N_CUSTOMERS = 1000
N_PRODUCTS = 300
N_ORDERS = 10000
N_REFUNDS = 500
DAYS = 90
RANDOM_SEED = 42
SOURCE_DATA_DIR = Path("data/source")

GENDERS = ["male", "female"]
AGE_GROUPS = ["10s", "20s", "30s", "40s", "50s", "60s"]
REGIONS = ["Seoul", "Gyeonggi", "Busan", "Daegu", "Incheon", "Daejeon", "Gwangju"]
CUSTOMER_GRADES = ["bronze", "silver", "gold", "vip"]
CUSTOMER_GRADE_WEIGHTS = [60, 25, 10, 5]

LAST_NAMES = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoon", "Jang", "Lim", "Han"]
FIRST_NAMES = [
    "Minjun",
    "Seoyeon",
    "Jiho",
    "Haeun",
    "Doyun",
    "Jiyu",
    "Hyunwoo",
    "Sumin",
    "Yejun",
    "Seojun",
]

PRODUCT_CATEGORIES = ["outer", "top", "bottom", "shoes", "bag", "accessory"]
PRODUCT_CATEGORY_WEIGHTS = [15, 30, 20, 15, 10, 10]
BRANDS = [
    "Aster",
    "Breez",
    "Covern",
    "Dailist",
    "Eunoia",
    "Fennec",
    "Grain",
    "Hale",
    "Ivero",
    "Juno",
]
BRAND_WEIGHTS = [18, 16, 14, 12, 10, 9, 8, 6, 4, 3]

CATEGORY_PRICE_RANGES = {
    "outer": (70000, 220000),
    "top": (18000, 80000),
    "bottom": (30000, 120000),
    "shoes": (50000, 180000),
    "bag": (40000, 200000),
    "accessory": (8000, 60000),
}

CATEGORY_ORDER_WEIGHTS = {
    "outer": 1.1,
    "top": 1.4,
    "bottom": 1.2,
    "shoes": 1.1,
    "bag": 0.9,
    "accessory": 0.8,
}

BRAND_ORDER_WEIGHTS = {
    "Aster": 1.35,
    "Breez": 1.25,
    "Covern": 1.2,
    "Dailist": 1.1,
    "Eunoia": 1.0,
    "Fennec": 0.95,
    "Grain": 0.9,
    "Hale": 0.85,
    "Ivero": 0.8,
    "Juno": 0.75,
}

PRODUCT_NAME_PARTS = {
    "outer": ["Wool Coat", "Padded Jacket", "Trench Coat", "Blazer"],
    "top": ["Cotton T-Shirt", "Oxford Shirt", "Knit Sweater", "Hoodie"],
    "bottom": ["Denim Pants", "Wide Slacks", "Cargo Pants", "Pleated Skirt"],
    "shoes": ["Leather Sneakers", "Chelsea Boots", "Loafers", "Running Shoes"],
    "bag": ["Mini Cross Bag", "Canvas Tote", "Leather Backpack", "Shoulder Bag"],
    "accessory": ["Ball Cap", "Silk Scarf", "Leather Belt", "Socks Set"],
}

PAYMENT_METHODS = ["card", "kakao_pay", "naver_pay", "bank_transfer"]
PAYMENT_METHOD_WEIGHTS = [55, 20, 20, 5]
REFUND_REASONS = ["size_issue", "defective", "change_of_mind", "delayed_delivery", "wrong_item"]
REFUND_REASON_WEIGHTS = [45, 15, 25, 10, 5]


def random_datetime_between(start: datetime, end: datetime) -> datetime:
    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, seconds))


def generate_customer_identity(index: int) -> tuple[str, str]:
    last_name = random.choice(LAST_NAMES)
    first_name = random.choice(FIRST_NAMES)
    customer_name = f"{last_name} {first_name}"
    email = f"{last_name.lower()}.{first_name.lower()}{index:03d}@example.com"
    return customer_name, email


def generate_customers(n_customers: int, now: datetime) -> list[dict]:
    customers = []
    signup_start = now - timedelta(days=365 * 2)

    for i in range(1, n_customers + 1):
        signup_datetime = random_datetime_between(signup_start, now)
        customer_name, email = generate_customer_identity(i)

        customer = {
            "customer_id": f"C{i:06d}",
            "customer_name": customer_name,
            "email": email,
            "gender": random.choice(GENDERS),
            "age_group": random.choice(AGE_GROUPS),
            "region": random.choice(REGIONS),
            "customer_grade": random.choices(
                CUSTOMER_GRADES,
                weights=CUSTOMER_GRADE_WEIGHTS,
                k=1,
            )[0],
            "signup_date": signup_datetime.date().isoformat(),
            "created_at": signup_datetime.isoformat(timespec="seconds"),
            "updated_at": signup_datetime.isoformat(timespec="seconds"),
        }

        customers.append(customer)

    return customers


def generate_products(n_products: int, now: datetime) -> list[dict]:
    products = []
    product_start = now - timedelta(days=365)

    for i in range(1, n_products + 1):
        category = random.choices(
            PRODUCT_CATEGORIES,
            weights=PRODUCT_CATEGORY_WEIGHTS,
            k=1,
        )[0]
        brand = random.choices(BRANDS, weights=BRAND_WEIGHTS, k=1)[0]
        price_min, price_max = CATEGORY_PRICE_RANGES[category]
        price = random.randrange(price_min, price_max + 1, 1000)
        cost = int(price * random.uniform(0.45, 0.7))
        created_datetime = random_datetime_between(product_start, now)
        name_part = random.choice(PRODUCT_NAME_PARTS[category])

        product = {
            "product_id": f"P{i:06d}",
            "product_name": f"{brand} {name_part}",
            "category": category,
            "brand": brand,
            "price": price,
            "cost": cost,
            "is_active": random.choices([True, False], weights=[95, 5], k=1)[0],
            "created_at": created_datetime.isoformat(timespec="seconds"),
            "updated_at": created_datetime.isoformat(timespec="seconds"),
        }

        products.append(product)

    return products


def is_sale_day(order_date: datetime) -> bool:
    return order_date.day in {1, 2, 3, 25, 26, 27, 28}


def order_date_weight(order_date: datetime) -> float:
    weight = 1.0

    if order_date.weekday() >= 5:
        weight *= 1.3

    if is_sale_day(order_date):
        weight *= 1.2

    return weight


def random_order_datetime(start: datetime, end: datetime) -> datetime:
    dates = []
    weights = []
    current = start.date()

    while current <= end.date():
        order_date = datetime.combine(current, datetime.min.time())
        dates.append(current)
        weights.append(order_date_weight(order_date))
        current += timedelta(days=1)

    selected_date = random.choices(dates, weights=weights, k=1)[0]
    hour = random.choices(
        list(range(24)),
        weights=[1, 1, 1, 1, 1, 2, 3, 5, 7, 8, 9, 9, 8, 8, 9, 10, 11, 12, 13, 12, 10, 7, 4, 2],
        k=1,
    )[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    order_datetime = datetime.combine(selected_date, datetime.min.time()).replace(
        hour=hour,
        minute=minute,
        second=second,
    )

    if order_datetime < start:
        return random_datetime_between(start, datetime.combine(selected_date, datetime.max.time()))

    if order_datetime > end:
        return random_datetime_between(datetime.combine(selected_date, datetime.min.time()), end)

    return order_datetime


def product_order_weight(product: dict) -> float:
    return (
        CATEGORY_ORDER_WEIGHTS[product["category"]]
        * BRAND_ORDER_WEIGHTS[product["brand"]]
    )


def select_order_products(products: list[dict], item_count: int) -> list[dict]:
    selected_products = []
    available_products = [product for product in products if product["is_active"]]

    for _ in range(item_count):
        weights = [product_order_weight(product) for product in available_products]
        product = random.choices(available_products, weights=weights, k=1)[0]
        selected_products.append(product)
        available_products.remove(product)

    return selected_products


def calculate_item_discount(quantity: int, unit_price: int, order_datetime: datetime) -> int:
    gross_amount = quantity * unit_price
    discount_rate = 0.0

    if is_sale_day(order_datetime):
        discount_rate += random.choice([0.05, 0.1, 0.15])
    elif random.random() < 0.25:
        discount_rate += random.choice([0.05, 0.1])

    return int(gross_amount * discount_rate)


def calculate_shipping_fee(subtotal_amount: int) -> int:
    if subtotal_amount >= 50000:
        return 0

    return 3000


def generate_orders_and_items(
    customers: list[dict],
    products: list[dict],
    n_orders: int,
    start: datetime,
    end: datetime,
) -> tuple[list[dict], list[dict]]:
    orders = []
    order_items = []
    order_item_index = 1

    for i in range(1, n_orders + 1):
        order_datetime = random_order_datetime(start, end)
        customer = random.choice(customers)
        item_count = random.choices([1, 2, 3, 4], weights=[55, 30, 12, 3], k=1)[0]
        selected_products = select_order_products(products, item_count)

        order_id = f"O{i:06d}"
        order_discount_amount = 0
        subtotal_amount = 0

        for product in selected_products:
            quantity = random.choices([1, 2, 3], weights=[80, 15, 5], k=1)[0]
            unit_price = product["price"]
            discount_amount = calculate_item_discount(quantity, unit_price, order_datetime)
            item_total_amount = quantity * unit_price - discount_amount
            order_discount_amount += discount_amount
            subtotal_amount += item_total_amount

            order_items.append(
                {
                    "order_item_id": f"OI{order_item_index:06d}",
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_amount": discount_amount,
                    "item_total_amount": item_total_amount,
                    "created_at": order_datetime.isoformat(timespec="seconds"),
                    "updated_at": order_datetime.isoformat(timespec="seconds"),
                }
            )
            order_item_index += 1

        shipping_fee = calculate_shipping_fee(subtotal_amount)
        total_amount = subtotal_amount + shipping_fee

        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_status": "completed",
                "order_datetime": order_datetime.isoformat(timespec="seconds"),
                "payment_method": random.choices(
                    PAYMENT_METHODS,
                    weights=PAYMENT_METHOD_WEIGHTS,
                    k=1,
                )[0],
                "total_amount": total_amount,
                "discount_amount": order_discount_amount,
                "shipping_fee": shipping_fee,
                "created_at": order_datetime.isoformat(timespec="seconds"),
                "updated_at": order_datetime.isoformat(timespec="seconds"),
            }
        )

    return orders, order_items


def update_order_refund_status(orders: list[dict], order_items: list[dict], refunds: list[dict]) -> None:
    orders_by_id = {order["order_id"]: order for order in orders}
    order_item_counts = Counter(item["order_id"] for item in order_items)
    refunded_item_counts = Counter(refund["order_id"] for refund in refunds)
    latest_refund_datetime_by_order = {}

    for refund in refunds:
        order_id = refund["order_id"]
        refund_datetime = refund["refund_datetime"]

        if order_id not in latest_refund_datetime_by_order:
            latest_refund_datetime_by_order[order_id] = refund_datetime
        else:
            latest_refund_datetime_by_order[order_id] = max(
                latest_refund_datetime_by_order[order_id],
                refund_datetime,
            )

    for order_id, refund_count in refunded_item_counts.items():
        order = orders_by_id[order_id]

        if refund_count == order_item_counts[order_id]:
            order["order_status"] = "refunded"
        else:
            order["order_status"] = "partially_refunded"

        order["updated_at"] = latest_refund_datetime_by_order[order_id]


def generate_refunds(
    orders: list[dict],
    order_items: list[dict],
    n_refunds: int,
    end: datetime,
) -> list[dict]:
    refunds = []
    orders_by_id = {order["order_id"]: order for order in orders}
    refundable_items = [
        item for item in order_items
        if datetime.fromisoformat(orders_by_id[item["order_id"]]["order_datetime"]) + timedelta(days=1) <= end
    ]
    refundable_items = random.sample(refundable_items, k=min(n_refunds, len(refundable_items)))

    for i, order_item in enumerate(refundable_items, start=1):
        order = orders_by_id[order_item["order_id"]]
        order_datetime = datetime.fromisoformat(order["order_datetime"])
        refund_start = order_datetime + timedelta(days=1)
        refund_end = min(order_datetime + timedelta(days=14), end)

        if refund_start > refund_end:
            refund_datetime = end
        else:
            refund_datetime = random_datetime_between(refund_start, refund_end)

        refund_amount = order_item["item_total_amount"]
        refund = {
            "refund_id": f"R{i:06d}",
            "order_id": order_item["order_id"],
            "order_item_id": order_item["order_item_id"],
            "refund_datetime": refund_datetime.isoformat(timespec="seconds"),
            "refund_amount": refund_amount,
            "refund_reason": random.choices(
                REFUND_REASONS,
                weights=REFUND_REASON_WEIGHTS,
                k=1,
            )[0],
            "created_at": refund_datetime.isoformat(timespec="seconds"),
            "updated_at": refund_datetime.isoformat(timespec="seconds"),
        }
        refunds.append(refund)
        order_item["updated_at"] = refund_datetime.isoformat(timespec="seconds")

    update_order_refund_status(orders, order_items, refunds)

    return refunds


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def print_customer_grade_distribution(customers: list[dict]) -> None:
    grade_counts = Counter(customer["customer_grade"] for customer in customers)

    print("customer_grade distribution:")
    for grade in CUSTOMER_GRADES:
        count = grade_counts[grade]
        ratio = count / len(customers) * 100
        print(f"- {grade}: {count} ({ratio:.1f}%)")


def print_product_distribution(products: list[dict]) -> None:
    category_counts = Counter(product["category"] for product in products)
    brand_counts = Counter(product["brand"] for product in products)

    print("product category distribution:")
    for category in PRODUCT_CATEGORIES:
        count = category_counts[category]
        ratio = count / len(products) * 100
        print(f"- {category}: {count} ({ratio:.1f}%)")

    print("top product brands:")
    for brand, count in brand_counts.most_common(5):
        ratio = count / len(products) * 100
        print(f"- {brand}: {count} ({ratio:.1f}%)")


def print_order_distribution(orders: list[dict], order_items: list[dict]) -> None:
    payment_counts = Counter(order["payment_method"] for order in orders)
    item_counts = Counter(item["order_id"] for item in order_items)
    average_order_amount = sum(order["total_amount"] for order in orders) / len(orders)
    average_items_per_order = sum(item_counts.values()) / len(orders)

    print("order payment distribution:")
    for payment_method in PAYMENT_METHODS:
        count = payment_counts[payment_method]
        ratio = count / len(orders) * 100
        print(f"- {payment_method}: {count} ({ratio:.1f}%)")

    print(f"average_order_amount: {average_order_amount:.0f}")
    print(f"average_items_per_order: {average_items_per_order:.2f}")


def print_refund_distribution(orders: list[dict], refunds: list[dict]) -> None:
    order_status_counts = Counter(order["order_status"] for order in orders)
    refund_reason_counts = Counter(refund["refund_reason"] for refund in refunds)
    refund_amount = sum(refund["refund_amount"] for refund in refunds)

    print("order status distribution:")
    for status in ["completed", "partially_refunded", "refunded"]:
        count = order_status_counts[status]
        ratio = count / len(orders) * 100
        print(f"- {status}: {count} ({ratio:.1f}%)")

    print("refund reason distribution:")
    for reason in REFUND_REASONS:
        count = refund_reason_counts[reason]
        ratio = count / len(refunds) * 100
        print(f"- {reason}: {count} ({ratio:.1f}%)")

    print(f"refund_amount: {refund_amount}")


def validate_generated_data(
    orders: list[dict],
    order_items: list[dict],
    refunds: list[dict],
) -> None:
    order_items_by_order_id = {}
    order_items_by_id = {}
    orders_by_id = {order["order_id"]: order for order in orders}

    for item in order_items:
        order_items_by_order_id.setdefault(item["order_id"], []).append(item)
        order_items_by_id[item["order_item_id"]] = item

    for order in orders:
        items = order_items_by_order_id[order["order_id"]]
        expected_total_amount = (
            sum(item["item_total_amount"] for item in items)
            + order["shipping_fee"]
        )

        if order["total_amount"] != expected_total_amount:
            raise ValueError(
                f"Invalid order total: {order['order_id']} "
                f"total_amount={order['total_amount']} "
                f"expected={expected_total_amount}"
            )

    refunded_order_item_ids = set()

    for refund in refunds:
        order_item_id = refund["order_item_id"]

        if order_item_id in refunded_order_item_ids:
            raise ValueError(f"Duplicate refund for order_item_id={order_item_id}")

        refunded_order_item_ids.add(order_item_id)
        order_item = order_items_by_id[order_item_id]

        if refund["refund_amount"] > order_item["item_total_amount"]:
            raise ValueError(
                f"Invalid refund amount: {refund['refund_id']} "
                f"refund_amount={refund['refund_amount']} "
                f"item_total_amount={order_item['item_total_amount']}"
            )

        if refund["refund_amount"] <= 0:
            raise ValueError(
                f"Invalid refund amount: {refund['refund_id']} "
                f"refund_amount={refund['refund_amount']}"
            )

        order_created_at = datetime.fromisoformat(orders_by_id[refund["order_id"]]["created_at"])
        refund_datetime = datetime.fromisoformat(refund["refund_datetime"])

        if refund_datetime < order_created_at:
            raise ValueError(
                f"Invalid refund datetime: {refund['refund_id']} "
                f"refund_datetime={refund['refund_datetime']} "
                f"order_created_at={order_created_at.isoformat(timespec='seconds')}"
            )

    print("validation passed")


def main() -> None:
    random.seed(RANDOM_SEED)

    now = datetime.now().replace(microsecond=0)
    order_start = now - timedelta(days=DAYS)
    customers = generate_customers(N_CUSTOMERS, now)
    products = generate_products(N_PRODUCTS, now)
    orders, order_items = generate_orders_and_items(
        customers,
        products,
        N_ORDERS,
        order_start,
        now,
    )
    refunds = generate_refunds(orders, order_items, N_REFUNDS, now)
    validate_generated_data(orders, order_items, refunds)
    write_csv(SOURCE_DATA_DIR / "customers.csv", customers)
    write_csv(SOURCE_DATA_DIR / "products.csv", products)
    write_csv(SOURCE_DATA_DIR / "orders.csv", orders)
    write_csv(SOURCE_DATA_DIR / "order_items.csv", order_items)
    write_csv(SOURCE_DATA_DIR / "refunds.csv", refunds)

    print(customers[:3])
    print(f"customers: {len(customers)}")
    print_customer_grade_distribution(customers)
    print(f"saved: {SOURCE_DATA_DIR / 'customers.csv'}")
    print(products[:3])
    print(f"products: {len(products)}")
    print_product_distribution(products)
    print(f"saved: {SOURCE_DATA_DIR / 'products.csv'}")
    print(orders[:3])
    print(f"orders: {len(orders)}")
    print(f"order_items: {len(order_items)}")
    print_order_distribution(orders, order_items)
    print(f"saved: {SOURCE_DATA_DIR / 'orders.csv'}")
    print(f"saved: {SOURCE_DATA_DIR / 'order_items.csv'}")
    print(refunds[:3])
    print(f"refunds: {len(refunds)}")
    print_refund_distribution(orders, refunds)
    print(f"saved: {SOURCE_DATA_DIR / 'refunds.csv'}")


if __name__ == "__main__":
    main()
