1. Chạy project
```bash
    ./run.sh
```
2. Kiến thức về mạng
- với lệnh ping sẽ truyền gói tin `icmp`
- trong docker sẽ dùng network `bridge` là mặc định
- các switch trong SDN phải hỗ trợ openflow
3. Onos
- vào ui qua đường dẫn: http://localhost:8183
    - username: onos
    - pasword: rocks
- xem version: `cat ~/onos/VERSION`
4. mininet
- xem version: `mn --version`
- chạy thử kết nối đến onos: `mn --controller=remote,ip=192.168.0.2,port=6653 --switch=ovs,protocols=OpenFlow13`
    - sử dụng OpenFlow13 phù hợp với onos phiên bản latest