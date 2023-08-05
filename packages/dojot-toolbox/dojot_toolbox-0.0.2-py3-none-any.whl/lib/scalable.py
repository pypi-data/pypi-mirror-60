class Scalable:
    def ask_replicas(self, component, use, default=1):
        if use:
            try:
                return int(input("How many replicas would you like for {}? [1] ".format( component )))
            except:
                return default 
        return default        