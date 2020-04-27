class UserLocationAndHealth:
    def __init__(self, latest_point_x, latest_point_y, person_id, user_health):
        self.latest_point_lat = str(latest_point_x),
        self.latest_point_lon = str(latest_point_y),
        self.person_id = int(person_id),
        self.user_health = str(user_health)

    def serialize(self):
        return {
                    'latest_lat': self.latest_point_lat[0],
                    'latest_lng': self.latest_point_lon[0],
                    'person_id': self.person_id[0],
                    'user_health': self.user_health,
                }

    def __repr__(self):
        return "{} {} {} {}".format(self.latest_point_lat,
                                    self.latest_point_lon,
                                    self.person_id,
                                    self.user_health)
