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
    - chọn phiên bản phù hợp, tìm tải file zip cho windows `windows-x86_64.zip` tại url release sau https://github.com/bazelbuild/bazel/releases
    - tải về giải nén và dẫn `PATH` vào thư mục này
- fix lỗi CRLF -> LF: 
    - với file java: `find . -name "*.java" -type f -exec dos2unix {} \;`
    - với tất cả các file: `find . -type f -exec dos2unix {} \;`
    - cấu hình git: `git config core.autocrlf false` cho local repo
4. mininet
- xem version: `mn --version`
- chạy thử kết nối đến onos: `mn --controller=remote,ip=192.168.0.2,port=6653 --switch=ovs,protocols=OpenFlow13`
    - sử dụng OpenFlow13 phù hợp với onos phiên bản latest