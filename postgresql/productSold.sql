CREATE OR REPLACE FUNCTION sendNoteProductSold()
RETURNS trigger AS
$$
DECLARE
    cur cursor for 
    select DISTINCT seller_users_id as "reciever" From product where id = NEW.id;

    mess VARCHAR;
BEGIN
    for elem in cur
    loop
        mess := concat('Vendeu  o Produto ', NEW.product_id ,' numa quantidade de ' , NEW.amount);
    insert into notifications(message,users_id,product_id)
    values(mess, elem.reciever, NEW.product_id);
    end loop;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER productSold
AFTER INSERT ON orders
FOR EACH ROW Execute PROCEDURE sendNoteProductSold();