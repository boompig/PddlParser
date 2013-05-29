(define (domain logistics-adl)
(:requirements :adl :domain-axioms)
(:types physobj - object
obj vehicle - phssobj
truck airplane - vehicle
location city - object
airport - location)
(:predicates (at ?x - physobj ?l - location)
(in ?x - obj ?t - vehicle)
(in-city ?l - location ?c - city)))