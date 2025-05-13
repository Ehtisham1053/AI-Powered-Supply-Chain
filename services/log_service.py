from models import db
from models.logs import Log
from models.user import User

class LogService:
    @staticmethod
    def get_logs(module=None, user_id=None, limit=100):
        """Get logs, optionally filtered by module and/or user"""
        try:
            query = Log.query
            
            if module:
                query = query.filter_by(module=module)
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            # Order by timestamp (newest first)
            query = query.order_by(Log.timestamp.desc())
            
            # Limit results
            if limit:
                query = query.limit(limit)
            
            logs = query.all()
            
            if not logs:
                return None, "No logs found"
            
            # Convert to list of dictionaries
            log_data = [log.to_dict() for log in logs]
            
            return log_data, None
        except Exception as e:
            return None, f"Error fetching logs: {str(e)}"
    
    @staticmethod
    def add_log(user_id, module, action, description, status):
        """Add a new log entry"""
        try:
            log = Log(
                user_id=user_id,
                module=module,
                action=action,
                description=description,
                status=status
            )
            db.session.add(log)
            db.session.commit()
            
            return True, "Log added successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error adding log: {str(e)}"
        


    @staticmethod
    def get_logs(module=None, user_id=None, limit=100):
        try:
            query = Log.query

            if module:
                query = query.filter_by(module=module)

            if user_id:
                query = query.filter_by(user_id=user_id)

            query = query.order_by(Log.timestamp.desc())

            if limit:
                query = query.limit(limit)

            logs = query.all()

            if not logs:
                return None, "No logs found"

            return [log.to_dict() for log in logs], None

        except Exception as e:
            return None, f"Error fetching logs: {str(e)}"
        

    @staticmethod
    def get_sales_logs(user_id=None, limit=100):
        return LogService.get_logs(module="sales", user_id=user_id, limit=limit)

