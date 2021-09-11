from __future__ import absolute_import, unicode_literals
# from celery import task
# from django.utils.timezone import now


# @task
# def runRMDP(unAsignerOrder):
#     print(unAsignerOrder)
#     delay = float('inf')
#     maxLengthPost: int = 10  # p_max
#     maxTimePost: int = 20  # minutes     #t_pmax
#     capacity: int = 10
#     velocity: int = 20
#     restaurantRepareTime: int = 10 * 60
#     deadlineTime :int = 40
#     instance = RMDP(delay, maxLengthPost, maxTimePost, capacity, velocity, restaurantRepareTime,deadlineTime)
#     currentTime = now()
#     instance.runRMDP([unAsignerOrder])
