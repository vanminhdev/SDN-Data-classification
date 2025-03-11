import requests
import json
import logging
import os
from typing import Dict, Any, Optional

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowRuleHandler:
    """
    Xử lý việc gọi API tới ONOS để cập nhật flow rule dựa trên kết quả phân loại
    """
    
    def __init__(self, onos_ip="localhost", onos_port=8181, username="onos", password="rocks"):
        """
        Khởi tạo FlowRuleHandler
        
        Args:
            onos_ip: Địa chỉ IP của ONOS controller
            onos_port: Port của ONOS REST API
            username: Tên đăng nhập ONOS
            password: Mật khẩu ONOS
        """
        self.onos_base_url = f"http://{onos_ip}:{onos_port}"
        self.flow_rule_update_url = f"{self.onos_base_url}/onos/v1/dataclassification/flowruleupdate/update"
        self.auth = (username, password)
        
        # Đọc cấu hình từ biến môi trường nếu có
        if os.environ.get('ONOS_IP'):
            self.onos_base_url = f"http://{os.environ.get('ONOS_IP')}:{os.environ.get('ONOS_PORT', onos_port)}"
            self.flow_rule_update_url = f"{self.onos_base_url}/onos/v1/dataclassification/flowruleupdate/update"
        
        if os.environ.get('ONOS_USERNAME') and os.environ.get('ONOS_PASSWORD'):
            self.auth = (os.environ.get('ONOS_USERNAME'), os.environ.get('ONOS_PASSWORD'))
            
        logger.info(f"Initialized FlowRuleHandler with ONOS API at {self.onos_base_url}")
    
    def update_flow_rule(self, packet_data: Dict[str, Any], service_type: str) -> bool:
        """
        Gửi yêu cầu cập nhật flow rule tới ONOS
        
        Args:
            packet_data: Thông tin gói tin
            service_type: Loại dịch vụ phân loại được (WEB, VIDEO, VOIP)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Chuẩn hóa service_type thành chữ thường
            service_type = service_type.lower()
            
            # Kiểm tra service_type hợp lệ
            valid_types = ["web", "video", "voip"]
            if service_type not in valid_types:
                logger.warning(f"Invalid service type: {service_type}. Using web as default.")
                service_type = "web"
            
            # Tạo payload cho request
            flow_rule_dto = {
                "deviceId": packet_data.get('device_id'),
                "ipSrc": packet_data.get('src_ip'),
                "ipDst": packet_data.get('dst_ip'),
                "serviceType": service_type
            }
            
            # Thêm thông tin cổng nếu có 
            if packet_data.get('src_port'):
                if packet_data.get('ip_proto') == 6:  # TCP
                    flow_rule_dto["tcpPortSrc"] = int(packet_data.get('src_port'))
                    flow_rule_dto["tcpPortDst"] = int(packet_data.get('dst_port'))
                elif packet_data.get('ip_proto') == 17:  # UDP
                    flow_rule_dto["udpPortSrc"] = int(packet_data.get('src_port'))
                    flow_rule_dto["udpPortDst"] = int(packet_data.get('dst_port'))
            
            # Log để debug
            logger.info(f"Sending flow rule update to ONOS with payload: {flow_rule_dto}")
            
            # Gửi request đến ONOS
            response = requests.post(
                self.flow_rule_update_url,
                auth=self.auth,
                json=flow_rule_dto,  # Gửi trực tiếp là JSON
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully updated flow rule for {service_type} service")
                return True
            else:
                logger.error(f"Failed to update flow rule. Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating flow rule: {str(e)}")
            return False
    
    def get_onos_status(self) -> Optional[Dict]:
        """
        Kiểm tra trạng thái của ONOS API
        
        Returns:
            Dict hoặc None: Trả về thông tin trạng thái nếu thành công, None nếu thất bại
        """
        try:
            status_url = f"{self.onos_base_url}/onos/v1/dataclassification/flowruleupdate/status"
            
            response = requests.get(
                status_url,
                auth=self.auth
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get ONOS status. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking ONOS status: {str(e)}")
            return None