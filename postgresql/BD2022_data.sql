CREATE TABLE users (
	id	 SERIAL,
	username	 VARCHAR(512) UNIQUE NOT NULL,
	email	 VARCHAR(512) UNIQUE NOT NULL,
	password	 VARCHAR(512) NOT NULL,
	isadmin	 BOOL,
	postalcode VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE seller (
	company	 VARCHAR(512),
	nif	 BIGINT UNIQUE NOT NULL,
	users_id INTEGER,
	PRIMARY KEY(users_id)
);

CREATE TABLE allorder (
	id		 SERIAL,
	buyer_users_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE notifications (
	id	 SERIAL,
	message	 VARCHAR(512) NOT NULL,
	users_id	 INTEGER NOT NULL,
	product_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE product (
	id		 SERIAL,
	item		 VARCHAR(512) NOT NULL,
	price		 FLOAT(8) NOT NULL,
	stock		 INTEGER NOT NULL,
	specs		 VARCHAR(512) NOT NULL,
	seller_users_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE rating (
	rating	 INTEGER,
	comment	 VARCHAR(512),
	product_id INTEGER NOT NULL,
	orders_id	 INTEGER UNIQUE NOT NULL
);

CREATE TABLE computers (
	cpu	 VARCHAR(512),
	gpu	 VARCHAR(512),
	ram	 INTEGER,
	product_id INTEGER,
	PRIMARY KEY(product_id)
);

CREATE TABLE smartphones (
	inches	 FLOAT(8),
	cpu	 VARCHAR(512),
	weight	 FLOAT(8),
	product_id INTEGER,
	PRIMARY KEY(product_id)
);

CREATE TABLE tv (
	inches	 FLOAT(8),
	weight	 FLOAT(8),
	fourk	 BOOL,
	product_id INTEGER,
	PRIMARY KEY(product_id)
);

CREATE TABLE versions (
	timeupdated	 TIMESTAMP NOT NULL,
	price	 FLOAT(8) NOT NULL,
	modifications VARCHAR(512),
	product_id	 INTEGER,
	item		 VARCHAR(512) NOT NULL,
	stock		 INTEGER NOT NULL,
	specs		 VARCHAR(512) NOT NULL,
	PRIMARY KEY(timeupdated,product_id)
);

CREATE TABLE buyer (
	nif	 BIGINT,
	users_id INTEGER,
	PRIMARY KEY(users_id)
);

CREATE TABLE commentsection (
	id	 SERIAL,
	comment	 VARCHAR(512),
	users_id	 INTEGER NOT NULL,
	product_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE orders (
	amount	 INTEGER NOT NULL,
	id		 SERIAL,
	product_id	 INTEGER NOT NULL,
	allorder_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE commentsection_commentsection (
	commentsection_id	 INTEGER,
	commentsection_id1 INTEGER NOT NULL,
	PRIMARY KEY(commentsection_id)
);

ALTER TABLE seller ADD CONSTRAINT seller_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE allorder ADD CONSTRAINT allorder_fk1 FOREIGN KEY (buyer_users_id) REFERENCES buyer(users_id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
--ALTER TABLE notifications ADD CONSTRAINT notifications_fk2 FOREIGN KEY (orders_id) REFERENCES orders(id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk2 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE product ADD CONSTRAINT product_fk1 FOREIGN KEY (seller_users_id) REFERENCES seller(users_id);
ALTER TABLE rating ADD CONSTRAINT rating_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE rating ADD CONSTRAINT rating_fk2 FOREIGN KEY (orders_id) REFERENCES orders(id);
ALTER TABLE computers ADD CONSTRAINT computers_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE smartphones ADD CONSTRAINT smartphones_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE tv ADD CONSTRAINT tv_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE versions ADD CONSTRAINT versions_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE buyer ADD CONSTRAINT buyer_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE commentsection ADD CONSTRAINT commentsection_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE commentsection ADD CONSTRAINT commentsection_fk2 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE orders ADD CONSTRAINT orders_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE orders ADD CONSTRAINT orders_fk2 FOREIGN KEY (allorder_id) REFERENCES allorder(id);
ALTER TABLE commentsection_commentsection ADD CONSTRAINT commentsection_commentsection_fk1 FOREIGN KEY (commentsection_id) REFERENCES commentsection(id);
ALTER TABLE commentsection_commentsection ADD CONSTRAINT commentsection_commentsection_fk2 FOREIGN KEY (commentsection_id1) REFERENCES commentsection(id);