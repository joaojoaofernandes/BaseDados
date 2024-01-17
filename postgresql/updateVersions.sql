CREATE OR REPLACE FUNCTION versions()
RETURNS trigger AS
$$
BEGIN
    Insert into versions(timeupdated, price, product_id, item, stock, specs)
    Values (current_timestamp(0), OLD.price, OLD.id, OLD.item, OLD.stock, OLD.specs);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER updateVersions
AFTER UPDATE OF item, price, stock, specs ON product
FOR EACH ROW Execute PROCEDURE versions();