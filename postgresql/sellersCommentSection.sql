CREATE OR REPLACE FUNCTION commentSectionComment()
RETURNS trigger AS
$$
DECLARE
    commentId commentsection.id%type;
    productId commentsection.product_id%type;
    usersId commentsection.users_id%type;
    mess VARCHAR;
BEGIN
    SELECT users_id,product_id into usersId, productId from commentsection where id = NEW.commentsection_id;
    mess := concat('Obteve uma resposta no comentário ', NEW.commentsection_id);
    insert into notifications(message, users_id, product_id)
    values(mess, usersId , productId);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER sellersCommentSection
AFTER INSERT ON commentsection_commentsection
FOR EACH ROW Execute PROCEDURE commentSectionComment();