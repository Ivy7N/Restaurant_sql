from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    reviews = relationship("Review", back_populates="customer")

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        highest_rating = 0
        fav_restaurant = None
        for review in self.reviews:
            if review.star_rating > highest_rating:
                highest_rating = review.star_rating
                fav_restaurant = review.restaurant
        return fav_restaurant

    def add_review(self, restaurant, rating):
        new_review = Review(restaurant=restaurant, customer=self, star_rating=rating)
        with Session(engine) as session:
            session.add(new_review)
            session.commit()

    def delete_reviews(self, restaurant):
        with Session(engine) as session:
            session.query(Review).filter_by(customer_id=self.id, restaurant_id=restaurant.id).delete()
            session.commit()


class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

    reviews = relationship("Review", back_populates="restaurant")

    @classmethod
    def fanciest(cls):
        with Session(engine) as session:
            return session.query(cls).order_by(cls.price.desc()).first()

    def all_reviews(self):
        review_strings = []
        for review in self.reviews:
            review_strings.append(review.full_review())
        return review_strings


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    star_rating = Column(Integer)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))

    customer = relationship("Customer", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."


engine = create_engine('sqlite:///restaurant.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
