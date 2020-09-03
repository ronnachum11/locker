from locust import HttpUser, task, between

class WebsiteTestUser(HttpUser):
    wait_time = between(0.5, 3.0)
    
    def on_start(self):
        self.client.post("/login", {"username":"admin", "password":"admin"})

    @task(1)
    def hello_world(self):
        self.client.get("/home")