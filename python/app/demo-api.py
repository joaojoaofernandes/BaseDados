##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2021/2022 ===============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors: 
##   Nuno Antunes <nmsa@dei.uc.pt>
##   BD 2022 Team - https://dei.uc.pt/lei/
##   University of Coimbra

 
from flask import Flask, jsonify, request
import logging, psycopg2, time, jwt
import datetime

SECRET_KEY = "hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH"

app = Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user = "aulaspl",
        password = "aulaspl",
        host = "db",
        port = "5432",
        database = "dbfichas"
    )
    
    return db



##########################################################
## ENDPOINTS
##########################################################


@app.route('/')
def landing_page():
    return """

    Hello World (Python)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2022 Team<br/>
    <br/>
    """

##################################################################
#                                                                #
#                                                                #
#                   PROJETO BASE DADOS 2022                      #
#                                                                #
#                                                                #   
##################################################################

##################################################################
#                                                                #
#                                                                #
#                      ADD USER                                  #
#                                                                #
#                                                                #   
##################################################################

#Adiciona um utilizador à tabela users e retorna o seu id
@app.route("/dbproj/user", methods=['POST'])
def add_user():
    logger.info("\n###              POST /user -> Add a new user              ###")

    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("Begin")
    logger.debug(f'payload: {payload}')
    
    statement = """INSERT INTO users (username, password, email, postalcode)
                VALUES (%s, %s, %s,%s) RETURNING id"""
    
    values = (payload["username"], payload["password"], payload["email"], payload["postalcode"])

    
    
    try:
        cur.execute(statement, values)

        user_id = cur.fetchone()[0]
        
        result = {'userId': user_id}
        
        #Verifica se é seller para o adicionar à tabela de sellers
        #se nao adiciona à tabela de buyers
        if(payload["seller"] == True):
            statement1 = """INSERT INTO seller (company, nif, users_id)
                    VALUES (%s, %s, %s)"""

            values1 = (payload["company"], payload["nif"], user_id)

            cur.execute(statement1, values1)
        else:
            statement1 = """INSERT INTO buyer (nif, users_id)
                    VALUES (%s, %s)"""

            values1 = (payload["nif"], user_id)

            cur.execute(statement1, values1)
            

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()

    return jsonify(result)


##################################################################
#                                                                #
#                                                                #
#                      LOGIN USER                                #
#                                                                #
#                                                                #   
##################################################################

#Verifica se o username existe e a password, retorna um autothoken se existir
@app.route("/dbproj/user", methods=['PUT'], strict_slashes=True)
def user_login():
    logger.info("###              PUT /user -> User Trying to Login             ###")

    login_user = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    
    logger.debug(f'Login information: {login_user}')
    
    
    try:
        statement =  """Select id from users where username = %s and password = %s"""
        values = (login_user["username"], login_user["password"])
        cur.execute(statement, values)
        id = cur.fetchone()[0]
        #Verifica se o id retornado existe ou nao
        if(id is not None):
            id = {'user_id': id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}

            result = jwt.encode(id,SECRET_KEY, algorithm="HS256")
            result = {'authToken': result}
        else:
            result = {'erro:':"User was not found, invalid username or password"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

##################################################################
#                                                                #
#                                                                #
#                          CREATE TV                             #
#                                                                #
#                                                                #   
##################################################################

#Cria um produto Tv e retorna o id do produto criado
@app.route("/dbproj/productTV", methods=['POST'], strict_slashes=True)
def createProductTv():
    logger.info("###              POST /user -> Seller Trying to add a Tv             ###")

    payload = request.get_json()

    #verifica se o token é valido
    login = authenticate(payload["token"])
    logger.info(payload["token"])
    logger.info(login)
    if(login[0] == False):
        return jsonify({'erro:': login[1]})


    id = login[1]
    logger.info(id)
    conn = db_connection()
    cur = conn.cursor()

    try:
        #verificar se o criador do produto é seller
        statement =  """Select users_id from seller where users_id = %s """
        values = (id, )
        cur.execute(statement, values)
        id = cur.fetchone()

        if(id is not None):
            #inserir o produto se o user for seller
            statement =  """Insert into product (item, price, stock, specs, seller_users_id)
                        values(%s, %s, %s, %s, %s) RETURNING ID"""

            values = (payload["item"],  payload["price"], payload["stock"],
                        payload["specs"], id)
            
            cur.execute(statement, values)

            product_id = cur.fetchone()[0]
            #verificar se conseguiu criar o produto e retornar o id
            if(product_id is not None):
                statement1 =  """Insert into tv (inches, weight, fourk, product_id)
                        values(%s, %s, %s, %s) RETURNING product_id"""

                values1 = (payload["inches"],  payload["weight"], payload["fourk"], product_id)
            
                cur.execute(statement1, values1)

                TvId = cur.fetchone()[0]
                if(TvId is not None):
                    result = {'productId': TvId}
                else:
                    result = {'erro:':"Product wasn't inserted"}
            else:
                result = {'erro:':"Product wasn't inserted"}

        else:
            result = {'erro:':"User is not a seller"}
    
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT");
            conn.close()

    return jsonify(result)


##################################################################
#                                                                #
#                                                                #
#                          CREATE PC                             #
#                                                                #
#                                                                #   
##################################################################
#Cria produto do tipo smartphone e retorna o seu PC
@app.route("/dbproj/productPC", methods=['POST'], strict_slashes=True)
def createProductPC():
    logger.info("###              POST /user -> Seller Trying to add a PC             ###")

    payload = request.get_json()
    #verifica se o token é valido
    login = authenticate(payload["token"])
    logger.info(payload["token"])
    logger.info(login)
    if(login[0] == False):
        return jsonify({'erro:': login[1]})


    id = login[1]
    logger.info(id)
    conn = db_connection()
    cur = conn.cursor()

    try:
        #verificar se o criador do produto é seller
        statement =  """Select users_id from seller where users_id = %s """
        values = (id, )
        cur.execute(statement, values)
        id = cur.fetchone()

        if(id is not None):
            #inserir o produto se o user for seller
            statement =  """Insert into product (item, price, stock, specs, seller_users_id)
                        values(%s, %s, %s, %s, %s) RETURNING ID"""

            values = (payload["item"],  payload["price"], payload["stock"],
                        payload["specs"], id)
            
            cur.execute(statement, values)

            product_id = cur.fetchone()[0]
            if(product_id is not None):
                result = {'productId': product_id}
                statement1 =  """Insert into computers (cpu, gpu, ram, product_id)
                        values(%s, %s, %s, %s) RETURNING product_id"""

                values1 = (payload["cpu"],  payload["gpu"], payload["ram"], product_id)
            
                cur.execute(statement1, values1)

                PCId = cur.fetchone()[0]
                if(PCId is not None):
                
                    result = {'productId': PCId}
                else:
                    result = {'erro:':"Product wasn't inserted"}
            else:
                result = {'erro:':"Product wasn't inserted"}

        else:
            result = {'erro:':"User is not a seller"}
    
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT");
            conn.close()

    return jsonify(result)

##################################################################
#                                                                #
#                                                                #
#                          CREATE SMARTPHONE                     #
#                                                                #
#                                                                #   
##################################################################
#Cria produto do tipo smartphone e retorna o seu id
@app.route("/dbproj/productTele", methods=['POST'], strict_slashes=True)
def createProductTele():
    logger.info("###              POST /user -> Seller Trying to add a SmartPhone             ###")

    payload = request.get_json()
    #verifica se o token é valido
    login = authenticate(payload["token"])
    logger.info(payload["token"])
    logger.info(login)
    if(login[0] == False):
        return jsonify({'erro:': login[1]})


    id = login[1]
    logger.info(id)
    conn = db_connection()
    cur = conn.cursor()

    try:
        #verificar se o criador do produto é seller
        statement =  """Select users_id from seller where users_id = %s """
        values = (id,)
        cur.execute(statement, values)
        id = cur.fetchone()
        if(id is not None):
            #inserir o produto se o user for seller
            statement =  """INSERT INTO product (item, price, stock, specs, seller_users_id)
                        VALUES(%s, %s, %s, %s, %s) RETURNING ID"""

            values = (payload["item"],  payload["price"], payload["stock"],
                        payload["specs"], id)
            
            cur.execute(statement, values)

            product_id = cur.fetchone()[0]
            if(product_id is not None):
                result = {'productId': product_id}
                statement1 =  """Insert into smartphones (inches, cpu, weight, product_id)
                        values(%s, %s, %s, %s) RETURNING product_id"""

                values1 = (payload["inches"],  payload["cpu"], payload["weight"], product_id)
            
                cur.execute(statement1, values1)

                TeleId = cur.fetchone()[0]
                if(TeleId is not None):
                
                    result = {'productId': TeleId}
                else:
                    result = {'erro:':"Product wasn't inserted"}
            else:
                result = {'erro:':"Product wasn't inserted"}

        else:
            result = {'erro:':"User is not a seller"}
    
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT");
            conn.close()

    return jsonify(result)

##################################################################
#                                                                #
#                                                                #
#                          UPDATE PRODUCT                        #
#                                                                #
#                                                                #   
##################################################################
#Faz update das informações do produto
@app.route("/dbproj/product/<idProduct>", methods=['PUT'], strict_slashes=True)
def updateProduct(idProduct):
    logger.info("###              POST /user -> Seller Trying to update a Product             ###")

    payload = request.get_json()
    #verifica se o token e valido
    login = authenticate(payload["token"])
    logger.info(payload["token"])
    logger.info(login)
    if(login[0] == False):
        return jsonify({'erro:': login[1]})


    id = login[1]
    logger.info(id)
    conn = db_connection()
    cur = conn.cursor()


    try:
        #Procura o produto tendo em conta o id do produto e o id do user
        statement = """SELECT item FROM product
        where product.id = %s and seller_users_id = %s FOR UPDATE"""
        values = (idProduct,id)

        cur.execute(statement,values)
        row = cur.fetchone()
        if(row is None):
            raise Exception("Invalid id or product is not from the logged user")


        #Se o produto existir e for do user autenticado faz update na tabela
        statement = """UPDATE product set item = %s, price = %s, stock = %s, specs = %s where id = %s"""
        values = (payload['item'], payload['price'], payload['stock'],payload['specs'], idProduct)
        cur.execute(statement, values)
        result ={'Sucess': "Product Updated"}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(result)


##################################################################
#                                                                #
#                                                                #
#                          BUY PRODUCT                           #
#                                                                #
#                                                                #   
##################################################################

#Compra um produto
@app.route("/dbproj/order", methods=['POST'], strict_slashes=True)
def order():
    logger.info("###              POST /user Trying to buy a Product             ###")

    payload = request.get_json()
    #Verifica se o token e valido
    login = authenticate(payload["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    id = login[1]
    conn = db_connection()
    cur = conn.cursor()
    try:
        #Verifica se o user e buyer
        statement =  """Select users_id from buyer where users_id = %s """
        values = (id,)
        cur.execute(statement, values)
        buyerId = cur.fetchone()
        #verifica se o buyerid existe
        if(buyerId is not None):
            #insere na tabela da lista de compras o id do buyer e recebe o id
            statement = ("""Insert into allorder (buyer_users_id) values(%s) RETURNING ID""")
            values = (id,)
            cur.execute(statement, values)
            orderId = cur.fetchone()[0]
            
            result = {}
            #percorre todos os itens do carrinho
            for i in range(len(payload['cart'])):
                
                #quantidade
                quantity = payload['cart'][i][1]
                #procura o produto
                statement = ("""SELECT price, stock FROM product
                            where product.id = %s FOR UPDATE""")
                values = (payload['cart'][i][0],)
                
                cur.execute(statement, values)
                row = cur.fetchone()
                logger.debug(row)
                
                #verifica se o produto existe
                if(row is not None):
                    stock = row[1]
                    #verifica se ha stock disponivel para ser comprado
                    if(stock >= quantity and quantity > 0):
                        stock = stock - payload["cart"][i][1]
                        statement = ("""Insert into orders (product_id, amount, allorder_id) values(%s, %s, %s)""")
                        values = (payload["cart"][i][0],payload["cart"][i][1], orderId)
                        cur.execute(statement, values)
                        statement = ("""UPDATE product set stock = %s where product.id = %s""")
                        values = (stock, payload['cart'][i][0])
                        cur.execute(statement, values)
                        result["OrderId : " + str(orderId) + " -> Purchase " + str(i+1)] = "Product " + str(payload['cart'][i][0]) + ": Bought"
                    
                    else:
                        result["Purchase " + str(i+1)] = "Product " + str(payload['cart'][i][0])+ ": insufficient stock"
                else:
                    result["Purchase " + str(i+1)] = "Product " + str(payload['cart'][i][0])+ ": Doesn't exist "
                
                
        else:
            result = {'erro:':"User is not a buyer"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(result)

##################################################################
#                                                                #
#                                                                #
#                          RATE PRODUCT                          #
#                                                                #
#                                                                #   
##################################################################

@app.route("/dbproj/rating/<productId>", methods=['POST'], strict_slashes=True)
def rating(productId): 
    logger.info("###              POST /user Trying to rate a Product             ###")

    payload = request.get_json()
    #Verifica se o token e valido
    login = authenticate(payload["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    id = login[1]
   
    conn = db_connection()
    cur = conn.cursor()
    try:
        #Procura o produto
        statement =  """Select id from product where id = %s """
        values = (productId,)
        cur.execute(statement, values)
        product = cur.fetchone()
        #verifica se o produto existe
        if(product is not None):
            #vai procurar o user a fazer o rate na tabela buyer
            statement =  """Select users_id from buyer where users_id = %s """
            values = (id,)
            cur.execute(statement, values)
            buyerId = cur.fetchone()
            #verifica se ele existe
            if(buyerId is not None):
                #procura o ultimo produto a ser comprado com aquele id
                statement =  """Select allorder_id from orders where product_id = %s ORDER BY allorder_id DESC"""
                values = (productId,)
                cur.execute(statement, values)
                _order_id = cur.fetchone()
                #se ele existir
                if(_order_id is not None):
                    #verifica se foi o buyer a comprar o produto
                    statement =  """Select buyer_users_id, id from allorder where id = %s"""
                    values = (_order_id,)
                    cur.execute(statement, values)
                    buyerId = cur.fetchone()[0]
                    #vai buscar o id da order unica do produto
                    statement =  """Select id from orders WHERE product_id = %s and allorder_id = %s ORDER BY id DESC"""
                    values = (productId,_order_id)
                    cur.execute(statement, values)
                    ordersId = cur.fetchone()
                    #Vai verificar se ja foi feito rating desse produto
                    statement =  """Select rating from rating where orders_id = %s"""
                    values = (ordersId,)
                    cur.execute(statement, values)
                    rating = cur.fetchone()
                    #se foi o user a comprar
                    if(buyerId == id):
                         #se ainda nao foi feito
                        if(rating is None):
                            #insere o rating
                            statement = ("""Insert into rating (rating, comment, orders_id,product_id) values(%s, %s, %s,%s) """)
                            values = (payload["rating"],payload["comment"], ordersId,productId)
                            cur.execute(statement, values)
                            result = {'Sucess:':"Rating done"}
                        else:
                            result={"erro": "Rating already done"}
                    else:
                        result ={"error": "User did not bought this Product"}
                else:
                    result ={"error": "Order does not exist"}
            else:
                result ={"error": "Not a Buyer"}
        else:
            result = {"error":"None product with id: " + str(productId)}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(result)

##################################################################
#                                                                #
#                                                                #
#                         LEAVE COMMENT                          #
#                                                                #
#                                                                #   
##################################################################
#faz um comentario e retorna o id dele
@app.route("/dbproj/questions/<productId>", methods=['POST'], strict_slashes=True)
def comment(productId): 
    logger.info("###              POST /user Trying to comment             ###")

    payload = request.get_json()
    #Verifica se o token e valido
    login = authenticate(payload["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    id = login[1]
    
    conn = db_connection()
    cur = conn.cursor()
    
    try:
        #Vai procurar o produto
        statement =  """Select id from product where id = %s """
        values = (productId,)
        cur.execute(statement, values)
        product = cur.fetchone()
        #verifica se existe
        if(product is not None):
            #deixa o comentario
            statement =  """Insert into commentsection (comment, users_id, product_id) values(%s, %s, %s) RETURNING ID"""
            values = (payload["question"],id, product)
            cur.execute(statement, values)
            commentId = cur.fetchone()[0]
            result = {"sucess": "Comment done Id: " + str(commentId)}
        else:
            result = {"error":"None product with id: " + str(productId)}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(result)

##################################################################
#                                                                #
#                                                                #
#                      RESPOND TO COMMENT                        #
#                                                                #
#                                                                #   
##################################################################
#responde a um comentario e retorna o seu id
@app.route("/dbproj/questions/<productId>/<commentId>", methods=['POST'], strict_slashes=True)
def commentResponse(productId,commentId): 
    logger.info("###              POST /user Trying to comment             ###")

    payload = request.get_json()
    #verifica se o user e valido
    login = authenticate(payload["token"])
    if(login[0] == False):
        return jsonify({'erro:': login[1]})
    
    id = login[1]
   
    conn = db_connection()
    cur = conn.cursor()
    
    try:
        #procura o produto
        statement =  """Select id from product where id = %s """
        values = (productId,)
        cur.execute(statement, values)
        product = cur.fetchone()
        #verifica se ele existe
        if(product is not None):
            #procura o comentario
            statement =  """Select id from commentsection where id = %s """
            values = (commentId,)
            cur.execute(statement, values)
            comment = cur.fetchone()
            #verifica se ele existe
            if(comment is not None):
                #insere a resposta
                statement =  """Insert into commentsection (comment, users_id, product_id) values(%s, %s, %s) RETURNING ID"""
                values = (payload["question"],id, product)
                cur.execute(statement, values)
                responseId = cur.fetchone()[0]

                statement =  """Insert into commentsection_commentsection (commentsection_id, commentsection_id1) values(%s, %s) """
                values = (responseId,commentId)
                cur.execute(statement, values)
                result = {"sucess": "Comment done Id: " + str(responseId)}
            else:
                result = {"error":"None comment with id: " + str(commentId)}
        else:
            result = {"error":"None product with id: " + str(productId)}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(result)

##################################################################
#                                                                #
#                                                                #
#                      PRODUCT INFO                              #
#                                                                #
#                                                                #   
##################################################################
#responde a um comentario e retorna o seu id
@app.route("/dbproj/product/<productId>", methods=['GET'], strict_slashes=True)
def productInfo(productId): 
    logger.info("###              GET /Product Info             ###")

   
    conn = db_connection()
    cur = conn.cursor()
    result = {}
    try:
        statement =  """Select id, item, price, stock, specs, seller_users_id from product where id = %s """
        values = (productId,)
        cur.execute(statement, values)
        row = cur.fetchone()
        result["Produto Info"] = "id: " +  str(row[0]) + " item: " + row[1] + " price: " + str(row[2]) + "stock: " + str(row[3]) + " specs: " + row[4] + " seller: " + str(row[5])


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'erro:': str(error)}
    finally:
        if conn is not None:
            cur.execute("COMMIT")
            conn.close()
    return jsonify(result)

##########################################################
#                                                        #
#                                                        #
#                   User Authentication                  #
#                                                        #
#                                                        #
##########################################################
#valida o token dado
def authenticate(token):
    try:
        id = jwt.decode(token,SECRET_KEY, algorithms=["HS256"])
        return True, id['user_id']
    except jwt.ExpiredSignatureError:
        msg = 'Signature has expired.'
        return False, msg
    except jwt.DecodeError:
        msg = 'Invalid Login Token Signature'
        return False,  msg
    except jwt.InvalidTokenError:
        msg = 'Invalid token.'
        return False,  msg

##########################################################
#                                                        #
#                      MAIN                              #
#                                                        #
##########################################################
if __name__ == "__main__":
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    time.sleep(1)

    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.1 online: http://localhost:8080/departments/\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)



