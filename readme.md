# SDN Data Classification

## 1. Chạy project

```bash
    ./run.sh
```

## 2. Kiến thức về mạng

- với lệnh ping sẽ truyền gói tin `icmp`
- trong docker sẽ dùng network `bridge` là mặc định
- các switch trong SDN phải hỗ trợ openflow
- EtherType trong header các gói tin
  - EtherType (Ethernet Type) là một trường trong tiêu đề Ethernet Frame (gói tin Ethernet) mà xác định kiểu dữ liệu hoặc giao thức mạng được đóng gói bên trong frame Ethernet. Trường EtherType giúp thiết bị mạng biết cách xử lý gói tin Ethernet và định dạng dữ liệu nó chứa
  - Các giá trị EtherType khác nhau xác định các loại dữ liệu khác nhau. Dưới đây là một số giá trị EtherType quan trọng:
    - `ARP` (Address Resolution Protocol): Giá trị EtherType cho gói tin ARP là 0x0806. ARP được sử dụng để ánh xạ địa chỉ IP sang địa chỉ MAC trong mạng.
    - `RARP` (Reverse ARP): Giá trị EtherType cho gói tin RARP là 0x8035. RARP được sử dụng để ánh xạ địa chỉ MAC thành địa chỉ IP.
    - `IPv4` (Internet Protocol version 4): Giá trị EtherType cho gói tin IPv4 là 0x0800. Điều này cho biết rằng gói tin chứa dữ liệu IP và có thể được định tuyến bằng cách sử dụng địa chỉ IP.
    - `IPv6` (Internet Protocol version 6): Giá trị EtherType cho gói tin IPv6 là 0x86DD. Đây là dành cho phiên bản IPv6 của giao thức Internet.
    - `LLDP` (Link Layer Discovery Protocol): Giá trị EtherType cho gói tin LLDP là 0x88CC. LLDP được sử dụng để giao tiếp và truyền tải thông tin về các thiết bị mạng và cổng nối trong mạng.
      - Gói tin LLDP phát ra từ các thiết bị mạng, chẳng hạn như switch và router, nhằm thông báo thông tin về chính chúng và cổng nối của chúng đến các thiết bị mạng khác
    - `VLAN Tagged Frames`: Các gói tin Ethernet có thẻ VLAN có giá trị EtherType là 0x8100 hoặc 0x88A8, tùy thuộc vào dạng VLAN (802.1Q hoặc 802.1ad).
    - `QINQ` (Double Tagging or QinQ VLAN): Giá trị EtherType cho Double Tagging (QinQ) là 0x88A8. QinQ (còn được gọi là IEEE 802.1ad) là một phương pháp để mở rộng số lượng VLAN trong mạng Ethernet bằng cách thêm một tag VLAN bổ sung vào các Ethernet Frame đã có một tag VLAN. Trường EtherType giúp thiết bị mạng hiểu cách xử lý các Ethernet Frame chứa đôi tag VLAN này
    - `BSN` (Big Switch Networks): Giá trị EtherType cho Big Switch Networks (BSN) là 0x8902. BSN là một công ty chuyên về giải pháp mạng dựa trên phần mềm (SDN - Software-Defined Networking). Giao thức BSN được sử dụng để truyền thông giữa các thành phần của hệ thống SDN của Big Switch Networks
    - `PPPOED` (PPPoE Discovery Stage): Giá trị EtherType cho PPPoE Discovery Stage là 0x8863. PPPoE (Point-to-Point Protocol over Ethernet) là một giao thức được sử dụng trong mạng Internet để thiết lập và quản lý kết nối điểm-điểm trên giao diện Ethernet. Trong quá trình khởi động kết nối PPPoE, gói tin PPPoE Discovery Stage có EtherType này được sử dụng để tìm kiếm và định danh máy chủ PPPoE
- Một gói tin `TCP` có gì
  - Một gói tin TCP (Transmission Control Protocol) bao gồm nhiều trường thông tin trong header và có thể chứa dữ liệu. Dưới đây là các thông tin chính trong một gói tin TCP:

    1. Port Numbers (Cổng nguồn và cổng đích): Cổng nguồn và cổng đích xác định ứng dụng nguồn và đích mà gói tin TCP đang gửi đến hoặc nhận từ. Cổng nguồn và cổng đích là các số 16-bit.

    2. Sequence Number (Số thứ tự): Xác định số thứ tự của gói tin trong chuỗi. Điều này giúp xác định thứ tự của các gói tin và đảm bảo chúng đến đúng thứ tự.

    3. Acknowledgment Number (Số xác nhận): Số này được sử dụng để xác định gói tin mà máy chủ hoặc máy khách muốn xác nhận là đã nhận được. Nó thường được sử dụng trong quá trình xác định trạng thái kết nối.

    4. Data Offset (Header Length): Trường này xác định độ dài của header TCP, được biểu diễn dưới dạng số từ 4-byte words.

    5. Flags (Cờ điều khiển): Các cờ điều khiển (bit flags) bao gồm các thông tin về trạng thái và điều khiển của gói tin TCP. Ví dụ, các cờ bao gồm cờ SYN (synchronization), cờ ACK (acknowledgment), cờ FIN (finish), và nhiều cờ khác.

    6. Window Size (Cửa sổ cơ hội): Xác định kích thước cửa sổ mà bên nhận có sẵn để nhận gói tin. Nó liên quan đến cách kiểm soát luồng và tránh quá tải mạng.

    7. Checksum (Kiểm tra tổng): Được sử dụng để kiểm tra tính toàn vẹn của gói tin và header. Nó giúp xác định xem gói tin có bị biến đổi trong quá trình truyền tải không.

    8. Urgent Pointer (Trỏ đến phần ưu tiên): Trường này thường sử dụng khi cờ URG (urgent) được đặt, và nó xác định vị trí của dữ liệu ưu tiên trong gói tin.

    9. Options (Tùy chọn): Có thể bao gồm các tùy chọn bổ sung như Maximum Segment Size (MSS), Timestamps, Selective Acknowledgment (SACK), và nhiều tùy chọn khác.

    10. Data (Dữ liệu): Phần này chứa dữ liệu thực sự mà gói tin TCP đang chuyển tải, nếu có.
- Địa chỉ IPv4:
  - Một địa chỉ IPv4 gồm 32 bit, thường được hiển thị dưới dạng 4 octet (8 bit mỗi octet), ví dụ: 192.168.1.5
  
  - Subnet Mask và Prefix:
    - Prefix (tiền tố) là cách viết tắt của subnet mask, cho biết bao nhiêu bit từ trái sang phải được sử dụng để xác định mạng
    - Prefix /32 nghĩa là tất cả 32 bit đều được sử dụng để xác định mạng
  
  - Ý nghĩa của các giá trị prefix thông dụng:
    - `/24` = `255.255.255.0` = 24 bit đầu tiên xác định mạng, 8 bit còn lại xác định host
    - `/16` = `255.255.0.0` = 16 bit đầu tiên xác định mạng, 16 bit còn lại xác định host
    - `/8` = `255.0.0.0` = 8 bit đầu tiên xác định mạng, 24 bit còn lại xác định host
    - `/32` = `255.255.255.255` = tất cả 32 bit xác định mạng, 0 bit xác định host

## 3. Onos

- vào ui qua đường dẫn: <http://localhost:8181/onos/ui/>
  - username: onos
  - pasword: rocks
- xem version: `cat ~/onos/VERSION`: `2.7.1`
- tạo project:
  - clone project onos: `https://github.com/opennetworkinglab/onos.git`
  - chạy lệnh: `bash "<đường dẫn tới project onos>/tools/dev/bin/onos-create-app"`
    - đặt tên groupId: domain tổ chức
    - đặt tên artifactId: tên app viết thường
    - tên package: kết hợp domain tổ chức và tên app
- build:
  - build và test: `mvn clean install`
  - buid oar:
    - trong file `pom.xml` uncomment các phần `onos.app.*` và điền thông tin phù hợp
    - chạy lại lệnh `mvn clean install`
    - sau khi chạy xong sẽ có thêm file `.oar` để cài đặt
- install app:
  - chạy lênh: `/root/onos/bin/onos-app localhost install! <tên app>.oar`
- debug:
  - mở project bằng intellij
  - thêm run/debug config:
    - chọn Remote JVM Debug
    - đăt tên cho config
    - để các cấu hình mặc định
        ![config-intellij-debug](./assets/config-intellij-remote-debug.png)
  - thêm environment: `JAVA_TOOL_OPTIONS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005 $JAVA_TOOL_OPTIONS"`
- cài bazel:
  - chọn phiên bản phù hợp, tìm tải file zip cho windows `windows-x86_64.zip` tại url release sau <https://github.com/bazelbuild/bazel/releases>
  - tải về giải nén và dẫn `PATH` vào thư mục này
- fix lỗi CRLF -> LF:
  - với file java: `find . -name "*.java" -type f -exec dos2unix {} \;`
  - với tất cả các file: `find . -type f -exec dos2unix {} \;`
  - cấu hình git: `git config core.autocrlf false` cho local repo
- kích hoạt app:
  - cấu hình qua environment variable `ONOS_APPS`, lưu ý sẽ bị lỗi app đầu và app cuối nên để cuối cùng bằng dấu `,`
    - vd: `ONOS_APPS="drivers,hostprovider,lldpprovider,gui2,vn.edu.huce.data-classification,fwd,openflow,"`
  - `Reactive Forwarding` - `org.onosproject.fwd`: có tác dụng xử lý chuyển tiếp gói tin mạng dựa trên cơ sở phản ứng. Thay vì cấu hình trước một bảng chuyển tiếp (flow table) để xử lý gói tin, Reactive Forwarding xác định cách xử lý gói tin dựa trên sự phản ứng của mạng khi gói tin đến. Kịch hoạt ứng dụng này thì có thể ping được
  - `OpenFlow Provider Suite` - `org.onosproject.openflow`: là một tập hợp các ứng dụng cung cấp khả năng hỗ trợ giao thức OpenFlow, một giao thức quản lý mạng SDN phổ biến. Nó cho phép ONOS tương tác với các thiết bị mạng (switches và routers) hỗ trợ OpenFlow để cấu hình và điều khiển chúng.
- packet processor
  - thêm app implement interface `PacketProcessor`
  - chỉ bắt các packet có length lớn hơn 100 để bỏ qua các packet thiết lập kết nối không cần thiết
- giải thích các hàm:
  - `payload.serialize()` <https://javadoc.io/static/org.onosproject/onos-api/1.13.0/org/onlab/packet/IPv4.html#serialize--> : return a byte[] containing this packet and payloads
- cấu hình webapi lần đầu
  - cấu hình `properties` trong file `pom.xml`

    ```xml
    <properties>
      ...
      <web.context>/onos/v1/dataclassification</web.context>
      <api.version>1.0.0</api.version>
      <api.title>Data Classification REST API</api.title>
      <api.description>APIs for data classification.</api.description>
      <api.package>vn.edu.huce.dataclassification.rest</api.package>
    <properties/>
    ```

  - cấu hình `instruction` trong file `pom.xml`

    ```xml
    <build>
      <plugins>
        ...
        <plugin>
          <groupId>org.apache.felix</groupId>
          <artifactId>maven-bundle-plugin</artifactId>
          <extensions>true</extensions>
          <configuration>
              <instructions>
                  <Bundle-SymbolicName>${project.artifactId}</Bundle-SymbolicName>
                  <_wab>src/main/webapp/</_wab>
                  <Include-Resource>WEB-INF/classes/apidoc/swagger.json=target/swagger.json,
                      {maven-resources}</Include-Resource>
                  <Web-ContextPath>${web.context}</Web-ContextPath>
              ...
              <instructions/>
          ...
          <configuration/>
        <plugin/>
      <plugins/>
    <build/>
    ```

  - Thêm file `web.xml` trong `src/webapp/WEB-INF/`
  - Viết các class api kế thừa `AbstractWebResource`

- Một số application:
  - Forwarding mặc định (Reactive Forwarding) `org.onosproject.fwd`
    - Chức năng:
      - Xử lý và định tuyến gói tin một cách tự động khi không có flow rule.
      - Dựa trên ARP và MAC để tìm đích của gói tin.
    - Ứng dụng:
      - Reactive Forwarding là ứng dụng ONOS mặc định giúp định tuyến nhanh.
- Cấu hình QoS dựa trên phân loại dịch vụ:
  - Để ứng dụng bên ngoài biết được các gói tin chạy qua những switch nào và áp dụng QoS phù hợp, cần xây dựng một quy trình để xác định đường đi của gói tin trong mạng và sau đó cài đặt QoS trên từng switch trong đường đi
  - Cách xác định gói tin đi qua switch nào:
    - Path Calculation:
        Sử dụng PathService để tính toán đường đi giữa hai thiết bị (host hoặc switch).
        ONOS sẽ sử dụng thông tin topology (như các link và switch) để trả về danh sách các switch và cổng tương ứng trong đường đi.
    - Packet Processor:
        Bằng cách xử lý các gói tin Packet-In, có thể lấy thông tin về các switch mà gói tin đã đi qua. từ đây có thể áp dụng QoS cho các switch nó đi qua hoặc điều chỉnh flow rule để đi qua các switch khác
  - ONOS hỗ trợ QoS thông qua việc sử dụng `Meter` hoặc `Queue` trên switch

## 4. mininet

- xem version: `mn --version`
- chạy thử mn: `mn --topo single,2 --controller=remote`
- chạy thử kết nối đến onos: `mn --controller=remote,ip=192.168.0.2,port=6653 --switch=ovs,protocols=OpenFlow13`
  - sử dụng OpenFlow13 phù hợp với onos phiên bản latest
- cấu hinh netplan
  - Trong phiên bản Ubuntu từ 17.10 trở đi mặc định Ubuntu đã chuyển từ sử dụng /etc/network/interfaces sang /etc/netplan/
- kiểm tra host đã cho phép chuyển gói tin qua:
  - `cat /proc/sys/net/ipv4/ip_forward`: nếu trả về 1 là cho phép
- cấu hình mạng
  - chạy file setup mạng:

    ```sh
    python3 /scripts/init_net.py
    ```

  - h1 route add default gw 10.0.0.1
  - h1 route -n
  - s1 ifconfig s1-eth1 10.0.0.2 netmask 255.0.0.0
  - s1 ip route
  - ip route show
  - ip route add
  - ip route del
  - iptables -L -v
  - traceroute 8.8.8.8
  - iptables-save
- giả lập http server cho một host
  - chạy http server:

    ```sh
    h4 python3 -m http.server 8000 &
    ```

  - request thử:

    ```sh
    h1 curl http://10.0.0.4:8000
    ```

- open vSwitch
  - Xem flows: chạy trong terminal container mininet

    ```sh
    ovs-ofctl -O OpenFlow13 dump-flows s1
    ```

  - Hàng đợi (queue) trong Open vSwitch được cấu hình và quản lý trên cổng (port) của switch
  - Mỗi cổng có thể có một hoặc nhiều hàng đợi được gắn với nó, và các luồng dữ liệu được định tuyến đến hàng đợi dựa trên cấu hình QoS
  - Nguyên tắc hoạt động của hàng đợi:
    - Mỗi cổng có thể có một cấu hình QoS riêng:
      - Một cổng trên switch có thể được gắn với một cấu hình QoS.
      - QoS quyết định cách lưu lượng mạng được phân phối vào các hàng đợi.
    - Hàng đợi được xác định bởi QoS:
      - Một cổng có thể có nhiều hàng đợi, được quản lý bởi QoS.
      - Mỗi hàng đợi có thể có các thông số như băng thông tối thiểu (min-rate) hoặc tối đa (max-rate), tùy thuộc vào yêu cầu lưu lượng.
    - Luồng dữ liệu được gắn với hàng đợi thông qua OpenFlow:
      - Sử dụng actions=set_queue:<queue_id> trong các quy tắc OpenFlow để chỉ định luồng dữ liệu nào sẽ được gửi vào hàng đợi nào.
  - Xem port

    ```sh
    ovs-vsctl list port
    ```

  - Giả sử bạn có một cổng s1-eth1 trên switch s1 và muốn kiểm tra cấu hình QoS:

    ```sh
    ovs-vsctl list port s1-eth1
    ```

  - Kiểm tra chi tiết QoS và các hàng đợi liên quan

    ```sh
    ovs-vsctl list qos
    ovs-vsctl list queue

    ovs-vsctl list qos s1-eth1
    ovs-vsctl list queue s1-eth1
    ```

  - Xem meters

    ```sh
    ovs-vsctl list-br

    ovs-ofctl -O OpenFlow13 dump-meters s1
    ```

  - Cấu hình meter:
    - Chỉ hỗ trợ các unit KB_PER_SEC (Kilo bit / s), PKTS_PER_SEC (packet / s) không hỗ trợ BYTES_PER_SEC (byte / s)
    - Band chỉ hỗ trợ DROP (giảm gói), REMARK (đánh dấu lại DSCP).
    - meter sẽ được áp dụng vào thông qua cấu hình flow

  - Đo băng thông

    ```sh
    h3 iperf -s &

    h1 iperf -c h3 -u -n 100B
    ```

## 5. influxdb

- Vào ui
  <http://localhost:8086>
  - tài khoản: admin/12345678

### Giới thiệu chung

InfluxDB là một cơ sở dữ liệu time series (dữ liệu chuỗi thời gian) mã nguồn mở, được thiết kế để xử lý khối lượng lớn dữ liệu time series với hiệu suất cao. InfluxDB đặc biệt phù hợp cho các ứng dụng giám sát, phân tích dữ liệu IoT, phân tích hiệu suất ứng dụng và các tình huống cần lưu trữ dữ liệu theo thời gian.

### Các khái niệm quan trọng

1. **Time Series Data**:
    - Dữ liệu được lập chỉ mục theo thời gian
    - Mỗi điểm dữ liệu bao gồm: timestamp, giá trị đo lường, và các thẻ đánh dấu

2. **Database**: Là container chứa dữ liệu, có thể chứa nhiều measurements

3. **Measurement**:
    - Tương tự như bảng trong cơ sở dữ liệu quan hệ
    - Lưu trữ dữ liệu liên quan đến một đối tượng cụ thể (VD: thông số mạng, hiệu suất hệ thống)

4. **Tags**:
    - Cặp key-value lưu trữ metadata
    - Được lập chỉ mục - tối ưu cho việc truy vấn
    - Dùng cho việc lọc và nhóm dữ liệu
    - VD: location=datacenter1, device_id=sw1

5. **Fields**:
    - Cặp key-value lưu trữ giá trị thực tế của dữ liệu
    - Không được lập chỉ mục
    - VD: bandwidth=100, latency=5ms

6. **Point**: Một bản ghi dữ liệu, bao gồm timestamp, tags và fields

7. **Retention Policy**:
    - Quy định thời gian lưu trữ dữ liệu
    - Giúp quản lý vòng đời dữ liệu và tối ưu hóa lưu trữ

8. **Continuous Queries**: Truy vấn tự động chạy định kỳ, thường dùng để tổng hợp dữ liệu

### Ngôn ngữ truy vấn

1. **InfluxQL**: Ngôn ngữ truy vấn tương tự SQL

  ```SQL
  SELECT bandwidth FROM network_stats WHERE device_id='sw1' AND time > now() - 1h
  ```

2. **Flux**: Ngôn ngữ truy vấn và xử lý dữ liệu mới hơn

  ```SQL
  from(bucket:"network")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "network_stats" and r.device_id == "sw1")
  ```

### Ưu điểm của InfluxDB trong môi trường SDN

- Hiệu suất cao khi xử lý dữ liệu time series
- Khả năng xử lý hàng triệu điểm dữ liệu mỗi giây
- Hỗ trợ tốt cho các tác vụ giám sát mạng thời gian thực
- Dễ dàng tích hợp với các công cụ hiển thị như Grafana
- Có cơ chế downsampling để lưu trữ hiệu quả dữ liệu lịch sử lâu dài
