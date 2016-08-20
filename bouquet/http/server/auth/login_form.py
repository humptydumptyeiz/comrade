from nevow import rend, tags, guard, loaders

class LoginForm(rend.Page):

	addSlash = True
	docFactory = loaders.stan(
	tags.html[
		tags.head[tags.title["Please log in to Comrade"]],
		tags.body[
			tags.form(action=guard.LOGIN_AVATAR, method="post")[
				tags.table[
					tags.tr[
						tags.td[ "Username:" ],
						tags.td[ tags.input(type='text',name='username') ],
					],
					tags.tr[
						tags.td[ "Password:" ],
						tags.td[ tags.input(type='password',name='password') ],
					]
				],
				tags.input(type='submit'),
			]
		]
	])

def logout(*args, **named):
	"""Null operation "logging out" the user"""