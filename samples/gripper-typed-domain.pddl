(define 
	(domain gripper-typed)
	(:requirements :typing)
	(:types room ball gripper)
	(:constants left right - gripper)
	(:predicates (at-robby ?r - room)
		(at ?b - ball ?r - room)
		(free ?g - gripper)
		(carry ?o - ball ?g - gripper))
	(:action move
		:parameters (?from ?to - room)
		:precondition (at-robby ?from)
		:effect 
			(and 
				(at-robby ?to)
				(not (at-robby ?from))
			)
	)
	(:action pick
		:parameters (?obj - ball ?room - room ?gripper - gripper)
		:precondition (and (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect 
			(and 
				(carry ?obj ?gripper)
				(not (at ?obj ?room))
				(not (free ?gripper))
			)
	)
)