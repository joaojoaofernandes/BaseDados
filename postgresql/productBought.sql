CREATE OR REPLACE FUNCTION sendNoteProductBought()
RETURNS trigger AS
$$
DECLARE 
    

    allorderId orders.allorder_id%type;
    buyerId allorder.buyer_users_id%type;

    mess VARCHAR;
BEGIN 
    SELECT allorder_id into allorderId from orders where id = NEW.id;
    SELECT buyer_users_id into buyerId from allorder where allorderId = NEW.id;
    
    mess := concat('Comprou o Produto ', NEW.product_id,' numa quantidade de ', NEW.amount);
    insert into notifications(message, users_id, product_id)
    values(mess, buyerId, NEW.product_id);

    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER productBought
AFTER INSERT ON orders
FOR EACH ROW Execute PROCEDURE sendNoteProductBought();