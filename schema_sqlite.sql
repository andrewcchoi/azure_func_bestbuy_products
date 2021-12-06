-- DROP TABLE IF EXISTS bestbuy.products;
DROP TABLE IF EXISTS products;


-- sqlserver
CREATE TABLE products (
 "id" INTEGER PRIMARY KEY AUTOINCREMENT
, "nextCursorMark" TEXT
, "total" INT
, "totalPages" INT
, "queryTime" REAL
, "totalTime" REAL
, "canonicalUrl" TEXT
, "sku" TEXT
, "name" TEXT
, "type" TEXT
, "startDate" TEXT
, "new" INT
, "activeUpdateDate" TEXT
, "active" INT
, "regularPrice" REAL
, "salePrice" REAL
, "clearance" INT
, "onSale" INT
, "categoryPath" TEXT
, "customerReviewCount" REAL
, "customerReviewAverage" REAL
, "priceUpdateDate" TEXT
, "itemUpdateDate" TEXT
, "class" TEXT
, "classId" TEXT
, "subclass" TEXT
, "subclassId" TEXT
, "department" TEXT
, "departmentId" TEXT
, "theatricalReleaseDate" INT
, "studio" TEXT
, "manufacturer" TEXT
, "modelNumber" TEXT
, "condition" TEXT
, "artistName" TEXT
, "images" TEXT
, "image" TEXT
, "color" TEXT
, "request_timestamp" TIMESTAMP NOT NULL
, "record_timestamp" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--ALTER TABLE products ADD CONSTRAINT DF_products DEFAULT SYSUTCDATETIME() FOR record_timestamp;

-- id INTEGER PRIMARY KEY AUTOINCREMENT,
-- username TEXT UNIQUE NOT NUL,
-- password TEXT NOT NULL
