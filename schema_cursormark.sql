-- DROP TABLE IF EXISTS bestbuy.products;
DROP TABLE IF EXISTS products;


-- sqlserver
CREATE TABLE products (
    "id" INT IDENTITY(1,1) PRIMARY KEY
    , "nextCursorMark" CHAR(36)
    , "total" INT
    , "totalPages" INT
    , "queryTime" FLOAT
    , "totalTime" FLOAT
    , "canonicalUrl" VARCHAR(256)
    , "sku" CHAR(8)
    , "name" VARCHAR(256)
    , "type" VARCHAR(8)
    , "startDate" DATE
    , "new" BIT
    , "activeUpdateDate" DATETIME2
    , "active" BIT
    , "regularPrice" FLOAT
    , "salePrice" FLOAT
    , "clearance" BIT
    , "onSale" BIT
    , "categoryPath" VARCHAR(512)
    , "customerReviewCount" FLOAT
    , "customerReviewAverage" FLOAT
    , "priceUpdateDate" DATETIME2
    , "itemUpdateDate" DATETIME2
    , "class" VARCHAR(20)
    , "classId" CHAR(3)
    , "subclass" VARCHAR(20)
    , "subclassId" CHAR(4)
    , "department" VARCHAR(20)
    , "departmentId" CHAR(2)
    , "theatricalReleaseDate" INT
    , "studio" VARCHAR(256)
    , "manufacturer" VARCHAR(30)
    , "modelNumber" VARCHAR(30)
    , "condition" VARCHAR(20)
    , "artistName" VARCHAR(256)
    , "images" VARCHAR(MAX)
    , "image" VARCHAR(256)
    , "color" VARCHAR(100)
    , "request_timestamp" DATETIME2 NOT NULL
    , "record_timestamp" DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- ALTER TABLE products ADD CONSTRAINT DF_products DEFAULT SYSUTCDATETIME() FOR record_timestamp;
