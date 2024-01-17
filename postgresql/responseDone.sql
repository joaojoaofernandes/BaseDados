CREATE OR REPLACE FUNCTION response()
RETURNS trigger AS
$$
DECLARE
    sellerID commentsection.users_id%type;
    mess VARCHAR;
BEGIN
    SELECT users_id into sellerID from commentsection where id = NEW.id;
    
    mess := concat('A secção de comentários do produto ', NEW.product_id, ' foi comentada');
    insert into notifications(message, users_id, product_id)
    values(mess, sellerID , NEW.product_id);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER sellersCommentSection
AFTER INSERT ON commentsection
FOR EACH ROW Execute PROCEDURE response();