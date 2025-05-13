from models import db
from models.procurement import ConfirmedPO
from models.po_supplier import POSupplier
from models.warehouse import Warehouse, WarehouseRequest
from datetime import datetime

class SupplierDashboardService:
    @staticmethod
    def get_supplier_confirmed_pos(supplier_id):
        try:
            pos = ConfirmedPO.query.filter_by(supplier_id=supplier_id).all()
            return [po.to_dict() for po in pos], None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def process_po(supplier_id, po_id, action):
        try:
            confirmed_po = ConfirmedPO.query.get(po_id)
            if not confirmed_po or confirmed_po.supplier_id != supplier_id:
                return False, "PO not found or unauthorized"

            item = confirmed_po.item
            quantity = confirmed_po.quantity

            # Confirm action
            if action == 'confirm':
                # Update warehouse
                warehouse = Warehouse.query.filter_by(item=item).first()
                if warehouse:
                    warehouse.stock += quantity
                    warehouse.last_updated = datetime.utcnow()
                else:
                    db.session.add(Warehouse(item=item, stock=quantity))

                # Remove related warehouse request if exists
                request = WarehouseRequest.query.filter_by(item=item).first()
                if request:
                    db.session.delete(request)

                status = 'confirmed'

            elif action == 'reject':
                status = 'rejected'
            else:
                return False, "Invalid action"

            # Record in po_supplier table
            db.session.add(POSupplier(
                item=item,
                supplier_id=supplier_id,
                quantity=quantity,
                status=status
            ))

            # Remove from confirmed_pos
            db.session.delete(confirmed_po)
            db.session.commit()

            return True, f"PO {status} successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
