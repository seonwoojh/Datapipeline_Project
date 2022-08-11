# <center>인터넷 쇼핑몰 리뷰를 활용한 NLP 감성분석 파이프라인 프로젝트</center>


<br/>
<br/>

## 목차

1. Kafka 클러스터 구성
    1. 아키텍처 구성도
    2. zookeeper 설정
    3. broker 설정
    4. zookeeper 및 kafka 서버 구동
    5. 토픽 생성
2. Kubernetes에 ELK 스택 구성하기 
    1. 전체 프로젝트 구조 및 아키텍처 구성도
    2. opensearch 구축
        1. Namespace 생성
        2. opensearch 마스터 노드 생성
        3. opensearch 데이터 노드 생성
        4. opensearch 인제스트 노드 생성
    3. Logstash 생성
        1. Logstash 구축
        2. 테스트
    4. Kibana 구축
        1. Kibana 생성
        2. 인덱스 패턴 추가
        3. 슬랙 알람 설정
        4. 분석데이터 인덱스 생성
        5. 대시보드 생성

---

## 1. Kafka 클러스터 구성

**아키텍처 구성도**

![kafka2.svg](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/31e2485d-46ff-4e17-be84-956c197cbfff/kafka2.svg)

 **zookeeper 설정**

각 인스턴스에 설치된 Kafka의 config/zookeeper.properties 파일은 하나의 Zookeeper를 실행하는데 쓰이는 설정 파일이다.

zookeeper1.properties, zookeeper2.properties, zookeeper3.properties 이런식으로 여러개의 설정파일을 만들고 하나의 장비에서 다중으로 실행할 수 있다는 의미이다. 설정파일을 다음과 같이 3대의 서버에 동일하게 추가한다.

새로 추가한 설정값은 클러스터를 구성하는데 필요한 설정 값들안데 여기서 주의할 점은 모든 Zookeeper 서버들은 동일한 변수 값을 가지고 있어야 한다.

```yaml
# 주키퍼의 트랜잭션 로그와 스냅샷이 저장되는 데이터 저장 경로(중요)
**dataDir=/tmp/zookeeper**

# 주키퍼 사용 TCP Port
clientPort=2181

# 팔로워가 리더와 초기에 연결하는 시간에 대한 타임 아웃 tick의 수
**initLimit=5**

# 팔로워가 리더와 동기화 하는 시간에 대한 타임 아웃 tick의 수(주키퍼에 저장된 데이터가 크면 수를 늘려야함)
**syncLimit=2**

# server.1에 자기 자신은 0.0.0.0 로 입력 ex) 2번서버일 경우 server.2가 0.0.0.0이 된다
# server.{1} -> {1} 은 myid이다 즉, server.myid 형식으로 되어있다.
**server.1=0.0.0.0:2888:3888

server.2=3.34.18.190:2888:3888

server.3=13.209.146.71:2888:3888**
```

- **dataDir :** server.1,2,3의 숫자는 인스턴스 ID이다. ID는 dataDir=/tmp/zookeeper 폴더에 myid파일에 명시가 되어야 한다. /tmp/zookeeper 디렉토리가 없다면 생성하고 myid 파일을 생성하여 각각 서버의 고유 ID값을 부여해야 한다.

```yaml
mkdir /tmp/zookeeper $ echo 1 > /tmp/zookeeper/myid (서버 1)
mkdir /tmp/zookeeper $ echo 2 > /tmp/zookeeper/myid (서버 2)
mkdir /tmp/zookeeper $ echo 3 > /tmp/zookeeper/myid (서버 3)
```

- **initLimit :** 팔로워가 리더와 초기에 연결하는 시간에 대한 타임아웃을 설정한다.
- **syncLimit :** 팔로워가 리더와 동기화 하는데에 대한 타임아웃. 즉 이 틱 시간안에 팔로워가 리더와 동기화가 되지 않는다면 제거 된다.
    - 이 두값은 dafault 기본값이 없기 때문에 반드시 설정해야 하는 값이다.
    
- **server.1,2,3 :** 각 서버의 IP주소와 Port를 설정한다. 여기서 중요한 점은 만약 1번 서버의 설정파일을 변경 중이라면 1번 서버, 즉 자기 자신에 대한 IP주소는 자신의 Public IP 주소가 아니라 0.0.0.0으로 설정해야 한다. zookeeper 설정 시 해당하는 노드가 localhost에 위치해 있는 경우, 예외상황 발생을 막기 위해 0.0.0.0으로 지정하는 것을 권장한다고 한다.

**broker 설정**

Kafka의 config/server.properties 파일은 하나의 Kafka를 실행하는데 쓰이는 설정 파일이다. Zookeeper와 마찬가지로 여러개의 설정파일을 만들고 다중 실행을 할 수 있다.

설정파일 config/server.properties에 3대 서버 각 환경에 맞는 정보를 입력해 준다.

```yaml
############################# Server Basics #############################
**broker.id=1**

############################# Socket Server Settings #############################

**listeners=PLAINTEXT://:9092 
advertised.listeners=PLAINTEXT://IP:9092**   
#listener.security.protocol.map=PLAINTEXT:PLAINTEXT,SSL:SSL,SASL_PLAINTEXT:SASL_PLAINTEXT,SASL_SSL:SASL_SSL 
# 보안 설정시 프로토콜 매핑 설정

num.network.threads=3       # 네트워크를 통한 처리를 할때 사용할 네트워크 스레드 개수 설정

# The number of threads that the server uses for processing requests, which may include disk I/O
num.io.threads=8        # 브로커 내부에서 사용할 스레드 개수 지정

############################# Log Basics #############################

log.dirs=/tmp/kafka-logs        # 통신을 통해 가져온 데이터를 파일로 저장할 디렉토리 위치. 티렉토리가 생성되어 있지 않으면 오류가 발생하므로 미리 생성해야함.

num.partitions=1                # 파티션의 개수를 명시하지 않고 토픽을 생성할때 기본 설정되는 파티션의 개수. 파티션의 개수가 많을수록 병렬처리 데이터 양이 늘어남

**log.retention.hours=-1**

log.segment.bytes=1073741824        # 브로커가 저장할 파일의 최대 크기 지정 데이터 양이 많아 이 크기를 채우게 되면 새로운 파일 생성

log.retention.check.interval.ms=300000     # 브로커가 저장한 파일을 삭제하기 위해 체크하는 간격을 지정

############################# Zookeeper #############################

**zookeeper.connect=server1-ip:2181,server2-ip:2181,server3-ip:2181**      

zookeeper.connection.timeout.ms=18000       # 주키퍼 세션 타임아웃 시간 설정
```

- **broker.id** : 실행할 브로커의 번호를 적는다. 클러스터를 구축할 때 브로커들을 구분하기 위해 단 하나 뿐인 번호로 설정해야 한다.
- **listeners** : 카프카 브로커가 통신을 위해 열어둘 인터페이스 IP, port, 프로토콜을 설정할 수 있다. 따로 설정하지 않으면 ANY로 설정된다.
- **advertised.listeners** : 카프카 클라이언트 또는 카프카 커맨드 라인 툴에서 접속할때 사용하는 IP와 port 정보를 설정한다.
- **log.retention.hours :** 브로커가 저장한 파일이 삭제되기까지 걸리는 시간을 설정한다. -1로 설정하면 영구보존된다.
- **zookeeper.connect :** 카프카 브로커와 연동할 주키퍼의 IP와 port를 설정한다.

**zookeeper 및 kafka 서버 구동**

Kafka를 구동하기 위해 먼저 Zookeeper를 구동 한다음 이후 Kafka를 구동해야 한다.

```yaml
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
bin/kafka-server-start.sh -daemon config/server.properties
```

**토픽 생성**

카프카에서 사용할 토픽을 생성한다. 토픽은 Naming Convention에 따라 생성해야하며, 이번 프로젝트에서는 쇼핑몰에 따라 토픽을 따로 생성하여 관리한다.

**Convention**

카프카에서는 토픽을 많이 생성해서 사용하는데 Naming Convention 없이 사용하게 된다면 나중에 복잡해질 수도 있기 때문에 토픽 생성시 주의해야한다.

카프카에서 토픽을 생성할 때 유효한 문자는 `영문, 숫자, 마침표, 쉼표, 언더바, 하이픈` 만 사용할 수 있다. 유의할 점은 마침표와 언더바는 충돌할 수 있기 때문에 둘 중 하나만 사용해야 한다.

이번 프로젝트에서는 <department name>.<team name>.<dataset name> 규칙에 따라 토픽을 생성한다. Naming Convention에 따른 쇼핑몰 토픽 목록은 다음과 같다.

```yaml
smartstore.goodnara.review (스마트 스토어 goodnara)
smartstore.drstyle.review (스마트 스토어 drstyle)
smartstore.thecheaper.review (스마트 스토어 thecheaper)
smartstore.180store.review (스마트 스토어 180store)
smartstore.cloony.review (스마트 스토어 cloony)
smartstore.theshopsw.review (스마트 스토어 theshopsw)
```

## 2. Kubernetes에 ELK 스택 구성하기

**전체 프로젝트 구조**

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/3286610f-bc98-4f0b-8c5e-1ad22e4384c1/Untitled.png)

**아키텍처 구성도**

![Opensearch.svg](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/c88e8393-67bc-4a2f-8067-6782ba3f942c/Opensearch.svg)

1. Namespace

EKS 클러스터 내에서 ELK 리소스들을 효율적으로 관리하기 위해 논리적 분리 단위인 `elk` 네임 스페이스를 생성했다.  이후 생성되는 모든 리소스들은 `namespace` 단위로 구분된다.

1. opensearch 

저장은 opensearch 가 담당한다. ELK 스택의 핵심은 opensearch 이며, 이 저장소를 기반으로 동작한다.  opensearch 는 루씬 기반의 검색 엔진이다

opensearch 클러스터에는 `마스터 노드` 3개와 `데이터 노드` 3개 , `인제스트 노드` 3개로 총 9개의 노드로 구성되어 있다. 

`마스터노드`와 `인제스트 노드`는 `Deployment` 방식으로 배포하여 `Pod`들을 관리하고,  데이터의 저장을 담당하는 `데이터 노드는` `Statefulset` 방식으로 생성하여 클러스터가 삭제되어도 데이터를 영구 보존할 수 있도록 설계했다.

마지막으로 Service는 마스터 노드와 데이터 노드는 `ClusterIP` 형태의 서비스로 구성하여 노드 간 통신은 가능하되 외부에서 접근할 수 없도록 설정하고, 인제스트 노드의 Service를 `NodePort` 형태로 배포하여 해당 노드를 통해서만 외부에서 접근 가능하도록 설정했다.

1. Kibana

Kibana를 통해 저장된 데이터를 `분석`하고 `시각화`한다. opensearch 에 저장된 쇼핑몰 리뷰 데이터에 대한 `Index 패턴`을 생성하고 `대시보드`를 통해 시각화한다. 로드밸런서 타입의 서비스를 생성하여 외부에서 접근이 가능했고, 로드밸런서 주소의 80번 포트로 접근하면 Kibana 클러스터에 접근할 수 있도록 구성했다.

1. Logstash

`Deployment` 방식으로 `Logstash Pod`를 배포하고 Nodeport 타입의 서비스로 배포하였다. 

Kafka input plugin을 이용하여 브로커에 적재된 쇼핑몰 데이터를 opensearch의 데이터 노드에 적재한다.

Logstash 파이프 라인 중 Filter 플러그인을 사용하여 정제하도록 구성했다.. Logstash를 통해 들어온 데이터는 `Message`라는 필드안에 한번에 들어오게 된다.

메세지 필드만 저장해도 되지만 추후 원활한 Kibana를 이용한 시각화를 위해 로그를 구분하여 각각의 `필드를 재생성`하는 필터를 추가한다.

### 2. Opensearch 구축

- Namespace 생성
- Opensearch 마스터 노드 생성
- Opensearch 데이터 노드 생성
- Opensearch 인제스트 노드 생성

1. Namespace 생성

 >> `namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
    name: elk
```

b. Opensearch 마스터 노드 생성

1. ConfigMap 생성

>> `elasticsearch-master-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: elk
  name: elasticsearch-master-config
  labels:
    app: elasticsearch
    role: master
data:
  elasticsearch.yml: |-
    cluster.name: ${CLUSTER_NAME}
    node.name: ${NODE_NAME}
    discovery.seed_hosts: ${NODE_LIST}
    cluster.initial_master_nodes: ${MASTER_NODES}
    network.host: 0.0.0.0
    node:
      master: true
      data: false
      ingest: false
    opendistro_security.ssl.http.enabled: false
    opendistro_security.disabled: true
```

Opensearch 설정 값을 가진 `ConfigMap`을 생성한다. 클러스터의 이름과 노드의 이름과 노드의 리스트를 통해 host를 찾도록 설정하고 `master: true` 옵션을 통해 마스터 노드로 생성한다.

1. Service 생성

>> `elasticsearch-master-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: elk
  name: elasticsearch-master
  labels:
    app: elasticsearch
    role: master
spec:
  ports:
  - port: 9300
    name: transport
  selector:
    app: elasticsearch
    role: master
```

마스터 노드에 대한 svc를 생성한다. 9300번 포트로 각 노드들과 통신할 수 있도록 설정했다.

1. Deployment 생성

>> `elasticsearch-master-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: elk
  name: elasticsearch-master
  labels:
    app: elasticsearch
    role: master
spec:
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
      role: master
  template:
    metadata:
      labels:
        app: elasticsearch
        role: master
    spec:
      nodeSelector:
        Name: Master 
      containers:
      - name: elasticsearch-master
        image: amazon/opendistro-for-elasticsearch:1.13.2
        imagePullPolicy: Always
        env:
        - name: CLUSTER_NAME
          value: elasticsearch
        - name: NODE_NAME
          value: elasticsearch-master
        - name: NODE_LIST
          value: elasticsearch-master,elasticsearch-data,elasticsearch-client
        - name: MASTER_NODES
          value: elasticsearch-master
        - name: "ES_JAVA_OPTS"
          value: "-Xms1G -Xmx1G"
        ports:
        - containerPort: 9300
          name: transport
        volumeMounts:
        - name: config
          mountPath: /usr/share/elasticsearch/config/elasticsearch.yml
          readOnly: true
          subPath: elasticsearch.yml
        - name: storage
          mountPath: /data
      volumes:
      - name: config
        configMap:
          name: elasticsearch-master-config
      - name: "storage"
        emptyDir:
          medium: ""
      initContainers:
      - name: increase-vm-max-map
        image: busybox
        command: ["sysctl", "-w", "vm.max_map_count=262144"]
        securityContext:
          privileged: true
```

Deployment로 Pod를 배포한다. opendistro-for-elasticsearch:1.13.2 버전을 사용하고, ES_JAVA_OPTS 를 1G로 설정했다. 

EKS의 master 노드 그룹에 배치하도록 `nodeSelector` 옵션을 추가하여 스케줄링 한다.

c. Opensearch 데이터 노드 생성

1. ConfigMap 생성

>> `elasticsearch-data-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: elk
  name: elasticsearch-data-config
  labels:
    app: elasticsearch
    role: data
data:
  elasticsearch.yml: |-
    cluster.name: ${CLUSTER_NAME}
    node.name: ${NODE_NAME}
    discovery.seed_hosts: ${NODE_LIST}
    cluster.initial_master_nodes: ${MASTER_NODES}
    network.host: 0.0.0.0
    node:
      master: false
      data: true
      ingest: false
    opendistro_security.ssl.http.enabled: false
    opendistro_security.disabled: true
```

`data: true` 옵션을 통해 데이터를 저장하는 노드로 설정한다.

1. Service 생성

>> `elasticsearch-data-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: elk
  name: elasticsearch-data
  labels:
    app: elasticsearch
    role: data
spec:
  ports:
  - port: 9300
    name: transport
  selector:
    app: elasticsearch
    role: data
```

1. Statefulset생성

>> `elasticsearch-data-statefulset.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  namespace: elk
  name: elasticsearch-data
  labels:
    app: elasticsearch
    role: data
spec:
  serviceName: "elasticsearch-data"
  selector:
    matchLabels:
      app: elasticsearch-data
      role: data
  replicas: 3
  template:
    metadata:
      labels:
        app: elasticsearch-data
        role: data
    spec:
      nodeSelector:
        Name: Data 
      containers:
      - name: elasticsearch-data
        image: amazon/opendistro-for-elasticsearch:1.13.2
        env:
        - name: CLUSTER_NAME
          value: elasticsearch
        - name: NODE_NAME
          value: elasticsearch-data
        - name: NODE_LIST
          value: elasticsearch-master,elasticsearch-data,elasticsearch-client
        - name: MASTER_NODES
          value: elasticsearch-master
        - name: "ES_JAVA_OPTS"
          value: "-Xms1G -Xmx1G"
        ports:
        - containerPort: 9300
          name: transport
        volumeMounts:
        - name: config
          mountPath: /usr/share/elasticsearch/config/elasticsearch.yml
          readOnly: true
          subPath: elasticsearch.yml
        - name: elasticsearch-data-persistent-storage
          mountPath: /data/db
        imagePullPolicy: Always
      volumes:
      - name: config
        configMap:
          name: elasticsearch-data-config
      initContainers:
      - name: increase-vm-max-map
        image: busybox
        command: ["sysctl", "-w", "vm.max_map_count=262144"]
        securityContext:
          privileged: true
  volumeClaimTemplates:
  - kind: PersistentVolumeClaim
    metadata:
      name: elasticsearch-data-persistent-storage
      annotations:
        volume.beta.kubernetes.io/storage-class: "gp2"
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: standard
      resources:
        requests:
          storage: 10Gi
```

`Statefulset`으로 `Pod`를 배포한다. PVC 템플릿을 이용해서 elasticsearch-data-persistent-storage라는 이름의 pvc를 생성한다.

d. Opensearch 인제스트 노드 생성

1. ConfigMap 생성

>> `elasticsearch-data-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: elk
  name: elasticsearch-client-config
  labels:
    app: elasticsearch
    role: client
data:
  elasticsearch.yml: |-
    cluster.name: ${CLUSTER_NAME}
    node.name: ${NODE_NAME}
    discovery.seed_hosts: ${NODE_LIST}
    cluster.initial_master_nodes: ${MASTER_NODES}
    network.host: 0.0.0.0
    node:
      master: false
      data: false
      ingest: true
    opendistro_security.ssl.http.enabled: false
    opendistro_security.disabled: true
```

`ingest: true` 옵션을 사용해 인제스트 노드로 설정한다.

1. Service 생성

>> `elasticsearch-client-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: elk
  name: elasticsearch-client
  labels:
    app: elasticsearch
    role: client
spec:
  ports:
  - port: 9300
    name: transport
  selector:
    app: elasticsearch
    role: client
```

>> `elasticsearch-client-http.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: elk
  name: elasticsearch-client-http
  labels:
    app: elasticsearch
    role: client
spec:
  type: NodePort
  ports:
  - port: 9200
    name: client
    targetPort: 9200
    nodePort: 30000
  selector:
    app: elasticsearch
    role: client
```

1. Deployment 생성

>> `elasticsearch-client-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: elk
  name: elasticsearch-client
  labels:
    app: elasticsearch
    role: client
spec:
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
      role: client
  template:
    metadata:
      labels:
        app: elasticsearch
        role: client
    spec:
      nodeSelector:
        Name: Client
      containers:
      - name: elasticsearch-client
        image: amazon/opendistro-for-elasticsearch:1.13.2
        env:
        - name: CLUSTER_NAME
          value: elasticsearch
        - name: NODE_NAME
          value: elasticsearch-client
        - name: NODE_LIST
          value: elasticsearch-master,elasticsearch-data,elasticsearch-client
        - name: MASTER_NODES
          value: elasticsearch-master
        - name: "ES_JAVA_OPTS"
          value: "-Xms4G -Xmx4G"
        ports:
        - containerPort: 9200
          name: client
        - containerPort: 9300
          name: transport
        volumeMounts:
        - name: config
          mountPath: /usr/share/elasticsearch/config/elasticsearch.yml
          readOnly: true
          subPath: elasticsearch.yml
        - name: storage
          mountPath: /data
      volumes:
      - name: config
        configMap:
          name: elasticsearch-client-config
      - name: "storage"
        emptyDir:
          medium: ""
      initContainers:
      - name: increase-vm-max-map
        image: busybox
        command: ["sysctl", "-w", "vm.max_map_count=262144"]
        securityContext:
          privileged: true
```

### 3. Logstash 구축

- logstash 생성

a. logstash 생성

1. ConfigMap 생성

>> `logstash-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: logstash-config
  namespace: elk
data:
  # logstash conf
  logstash.yml: |
    http.host: "0.0.0.0"
    path.config: /usr/share/logstash/pipeline
    config.reload.automatic: true

# logstash pipeline
  logstash.conf: |
```

Logstash 설정 값을 가진 `ConfigMap`을 생성한다. `logstash.yml` 설정파일에 `config.reload.automatic: true` 옵션으로 만약 설정 파일이 변경되면 자동으로 Logstash를 재시작 하도록 설정했다.

`logstash.conf`는 로그 데이터의 파이프 라인 설정 파일이다. 

>> Input

```yaml
input {
      kafka {
        bootstrap_servers => ""   # 브로커 주소 IP:9092
        topics => ["smartstore.goodnara.review","smartstore.drstyle.review","smartstore.thecheaper.review","smartstore.180store.review","smartstore.cloony.review","smartstore.theshopsw.review"]
        consumer_threads => 3   # 컨슈머 쓰레드(파티션 갯수와 동일)
        isolation_level => "read_committed"   # 트랜잭션 격리수준(폴링 메세지는 커밋된 트랜잭션 메세지만 반환한다.)
        value_deserializer_class => "org.apache.kafka.common.serialization.StringDeserializer"    # 레코드값 역직렬화에 사용되는 JAVA Class(String)
        auto_offset_reset => "earliest"   # 처음 브로커에 진입했을때, 데이터를 가지고오는 시작점을 지정한다. earliest는 초기에 consumer group이 설정되어 있지 않은 경우에만 적용되므로, 추후 컨슈머를 재시작 하더라도 데이터 중복 이슈를 해결할 수 있다.
        group_id => "smartstore" # 컨슈머 그룹이름을 지정한다.
      }
    }
```

- isolation_level : 트랜잭션 격리 수준을 설정한다. 폴링 메세지는 커밋된 트랜잭션 메세지만 반환한다.
- value_deserializer_class : 레코드값 역직렬화에 사용되는 JAVA Class(String)
- auto_offset_reset : Consumer group으로 처음 broker에 진입 했을때, 데이터를 가져오는 시작점을 지정할 수 있다. default 값은 latest로 설정되어 있다. 만약 broker에 데이터가 13시부터 15시까지 쌓여있고 consumer를 15시에 붙였다고 하면, 13시부터 15시까지의 데이터는 가져오지 않고 15시 이후의 데이터만 가져오게 된다.
    
    상황에 따라 데이터 누락이 발생할 수 있기 때문에 earliest로 설정한다. 
    
    earliest 설정은 broker에 컨슈머 그룹이 설정되어 있지 않은 경우에만 적용되므로, 새로 컨슈머 그룹이 생성되었다면 데이터의 처음부터 읽어 오게 된다.
    
    만약 기존 컨슈머 그룹이 지정된 상태에서 컨슈머를 재시작했다면, 컨슈머 그룹에 이미 오프셋 정보 및 메타 데이터가 남아있기 때문에 earliest 설정은 적용되지않고, 오프셋 정보를 시작점으로 데이터를 읽어오기 때문에 데이터 중복 이슈를 예방할 수 있다.
    
     
    

>> filter - `Timestamp`

```yaml
filter {
      # ----------------------- UTC(default) Timestamp -> KST Timestamp로 변환하기 -----------------
        mutate {
          add_field => {
            "timestamp" => ""   # timestamp 필드 생성(새로 생성된 필드의 기본 데이터 타입은 String이다.)
          }
        }
        # ruby 코드로 "@timestamp" 필드의 UTC 기준 현재 시간에 9시간을 더한 값을 timestamp 필드에 저장한다.
        ruby {
          code => "event.set('timestamp', event.get('@timestamp').time.localtime('+09:00').strftime('%Y-%m-%d %H:%M:%S'))"
        }
        # timestamp 필드의 데이터는 String이므로 날짜 형식으로 지정함(ISO8601)
        # ISO8601 = 2019-01-26T17:00:00.000Z
        date {
          match => ["timestamp", "ISO8601", "YYYY-MM-dd HH:mm:ss"]
          target => "timestamp"   # date 필터가 적용될 필드 지정
        }
        # timestamp를 파싱하여 yy mm dd만 추출해 yymmdd 필드로 저장한다.
        grok {
          match => {
            "timestamp" => "\d\d%{INT:yy}-%{MONTHNUM:mm}-%{MONTHDAY:dd}%{GREEDYDATA}"
          }
          # yymmdd를 메타필드로 저장한다.
          add_field => {
            "[@metadata][yymmdd]" => "%{yy}%{mm}%{dd}"
          }
        }
```

- Opensearch의 index를 일별로 생성하고 yyMMdd를 postfix로 설정하려고 한다. ex) index-220803 하지만 Logstash는 기본적으로 @timestamp를 UTC+0 표준시로 나타내기 때문에 한국 시간과는 약 9시간의 차이가 발생하게 된다.  따라서 UTC+0 를 KST(UTC+9)로 바꿔서 사용해야한다.

- 먼저 timestamp 필드를 생성한다. 이때 새로 생성되는 필드는 String 타입임을 기억하고 있어야한다.

- 이후 ruby 코드를 통해 @timestamp 필드의 현재 시간에 9시간을 추가하여 timestamp 필드에 저장한다.

- 필드에 값이 저장되었다면 date plugin을 통해 날짜 형식(ISO8601)으로 변환하고 timestamp를 파싱하여 yy mm dd 값만 추출해 메타 데이터의 yymmdd 필드로 저장한다.

>> filter - `message 필드 정제`

```yaml
# ------------------------- message 필드 정제 ----------------------
        # 정규표현식으로 특수문자 1차 제거한다.
        mutate {
          gsub => ["message", "[\"/{}]", ""]
        }
        # comma를 기준으로 메세지 필드를 나눈 후, colon을 기준으로 Key, value 형식으로 필드를 생성한다.
        kv {
          field_split => "," 
          value_split => ":"
        }
        # 사용하지 않을 필드들을 제거하고 필드의 이름을 재설정한다.
        mutate {
          remove_field => [ "port","@version","host","message","@timestamp", "yy", "mm", "dd" ]
          rename => {" comment" => "comment"}
          rename => {" date" => "date"}
          rename => { " star" => "star" }
        }
        # star 필드를 String에서 Integer 타입으로 변환한다.
        mutate {
          convert => {
            "star" => "integer"
          }
        }
    }
```

- 먼저 정규표현식을 이용하여 1차적으로 특수문자를 제거한다.
- kv 플러그인을 통해 comma를 기준으로 메세지 필드를 나눈 후, colon을 기준으로 Key, value 형식으로 필드를 생성한다.
- 이후 분석에 필요하지 않은 필드는 제거하고  필드의 이름을 재설정한다.
- 마지막으로 분석에 필요한 star(평점) 필드의 데이터 타입을 Integer로 변환한다.

>> `output`

```yaml
output {
      stdout { codec => rubydebug }
      # ------------- 쇼핑몰 토픽에 따라 인덱스를 나누어 저장한다. -------------
      # 스마트 스토어 모자 Topic
      if [topic] =~ "smartstore.goodnara.review" {
        elasticsearch {
          hosts => "http://elasticsearch-client-http.elk.svc.cluster.local:9200"
          index => "smartstore.goodnara.review-%{[@metadata][yymmdd]}"
          codec => "json"
          timeout => 120
        }
      } # if end
      else if [topic] =~ "smartstore.drstyle.review" {
        elasticsearch {
          hosts => "http://elasticsearch-client-http.elk.svc.cluster.local:9200"
          index => "smartstore.drstyle.review-%{[@metadata][yymmdd]}"
          codec => "json"
          timeout => 120
        }
      } # if end
      else if [topic] =~ "smartstore.thecheaper.review" {
        elasticsearch {
          hosts => "http://elasticsearch-client-http.elk.svc.cluster.local:9200"
          index => "smartstore.thecheaper.review-%{[@metadata][yymmdd]}"
          codec => "json"
          timeout => 120
        }
      } # if end
      # 스마트 스토어 티셔츠 Topic
      else if [topic] =~ "smartstore.180store.review" {
        elasticsearch {
          hosts => "http://elasticsearch-client-http.elk.svc.cluster.local:9200"
          index => "smartstore.180store.review-%{[@metadata][yymmdd]}"
          codec => "json"
          timeout => 120
        }
      } # if end
      else if [topic] =~ "smartstore.cloony.review" {
        elasticsearch {
          hosts => "http://elasticsearch-client-http.elk.svc.cluster.local:9200"
          index => "smartstore.cloony.review-%{[@metadata][yymmdd]}"
          codec => "json"
          timeout => 120
        }
      } # if end
      else if [topic] =~ "smartstore.theshopsw.review" {
        elasticsearch {
          hosts => "http://elasticsearch-client-http.elk.svc.cluster.local:9200"
          index => "smartstore.theshopsw.review-%{[@metadata][yymmdd]}"
          codec => "json"
          timeout => 120
        }
      } # if end
    } # output end
```

Opensearch에 토픽에 따라 인덱스를 나누어 저장하도록 설정했다. 앞서 생성했던 메타데이터 필드의 KST yymmdd 를 활용해 토픽이름-yymmdd 형식으로 인덱스를 저장하여 각 토픽에 대한 인덱스를 일자 별로 나누어 관리할 수 있도록 설정했다.

1. Service 생성

>> `logstash-svc-nodeport.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: logstash
  namespace: elk
spec:
  type: NodePort
  ports:
  - port: 5000
    targetPort: 5000
  selector:
    app: logstash
```

NodePort타입으로 서비스를 배포하고 Logstash의 5000 포트로 요청이 전송되도록 설정했다.

1. Deployment 생성

>> `logstash-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logstash
  namespace: elk
spec:
  replicas: 1
  selector:
    matchLabels:
      app: logstash
  template:
    metadata:
      labels:
        app: logstash

    spec:
      nodeSelector:
        Name: Logstash
      volumes:
        - name: logstash-config-volume
          configMap:
            name: logstash-config
            items:
              - key: logstash.yml
                path: logstash.yml
        - name: logstash-pipeline-volume
          configMap:
            name: logstash-config
            items:
              - key: logstash.conf
                path: logstash.conf
      containers:
        - name: logstash
          image: docker.elastic.co/logstash/logstash:7.10.2
          resources:
            limits:
              cpu: 2000m
              memory: 2Gi
            requests:
              cpu: 1500m
              memory: 1.5G
          env:
            - name: LS_JAVA_OPTS
              value: '-Xmx1G -Xms1G'
          ports:
            - name: tcp
              containerPort: 5000
              protocol: TCP
          volumeMounts:
            - name: logstash-config-volume
              mountPath: /usr/share/logstash/config

            - name: logstash-pipeline-volume
              mountPath: /usr/share/logstash/pipeline
```

nodeSelector 옵션으로 Logstash 노드 그룹으로 스케줄링 되도록 설정한다. 이후 Pod의 리소스를 설정하고 Logstash 컨테이너 포트를 5000번으로 변경한다. 마지막으로 앞서 설정했던 파이프라인 파일을 volumeMounts 옵션을 통해 마운트한다.

b. 테스트

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e59aa902-319a-4d1c-9e48-edd07f1911c7/Untitled.png)

쇼핑몰 리뷰 데이터가 성공적으로 적재된 것을 알 수 있다.

### 4. Kibana 구축

- kibana 생성
- 인덱스 패턴 추가
- 슬랙 알람 설정
- 분석 데이터 인덱스 생성
- 대시보드 생성

a. kibana 생성

1. ConfigMap 생성

>> `kibana-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: elk
  name: kibana-config
  labels:
    app: kibana
data:
  kibana.yml: |-
    server.host: 0.0.0.0
    elasticsearch:
      hosts: ${ELASTICSEARCH_HOSTS}
```

1. Service 생성

>> `kibana-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: elk
  name: kibana
  labels:
    app: kibana
spec:
  type: LoadBalancer
  ports:
  - port: 80
    name: webinterface
    targetPort: 5601
  selector:
    app: kibana
```

1. Deployment 생성

>> `kibana-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: elk
  name: kibana
  labels:
    app: kibana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kibana
  template:
    metadata:
      labels:
        app: kibana
    spec:
      nodeSelector:
        Name: Kibana
      containers:
      - name: kibana
        image: tjswl950/ek_kib01:pluginRemove
        command: 
        ports:
        - containerPort: 5601
          name: webinterface
        env:
        - name: ELASTICSEARCH_HOSTS
          value: "http://elasticsearch-client-http.elk.svc.cluster.local:9200"
        volumeMounts:
        - name: config
          mountPath: /usr/share/kibana/config/kibana.yml
          readOnly: true
          subPath: kibana.yml
      volumes:
      - name: config
        configMap:
          name: kibana-config
```

b. **인덱스 패턴 추가**

데이터 처리 및 분석을 위한 시각화를 만들기 전에 Kibana에 `인덱스 패턴`을 설정해야 한다. 인덱스 패턴은 검색 및 분석을 실행하는 `opensearch Index`를 식별하거나 필드를 설정하는데 사용한다. 인덱스 패턴은 여러 인덱스에 대응할 수 있는 선택적 `와일드 카드`를 포함한 문자열이다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/af5505b3-d8c8-4c46-a457-b1f3c7da0c75/Untitled.png)

Kibana에 접속해서 `Discover` 탭에 들어가면 새로운 인덱스 패턴을 추가할 수 있다. 

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/05801790-088f-4aea-b157-85b889c8ed56/Untitled.png)

인덱스 패턴을 `smartstore*`로 설정한다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/001199d0-3505-4238-9b36-b59dc8952431/Untitled.png)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/fb46eb7f-de8d-4023-8fdf-5b4a67b30a5c/Untitled.png)

time field를 timestamp로 설정하고 생성 버튼을 누르면 성공적으로 인덱스 패턴이 생성된다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/92e7fa35-a382-4c6d-8a68-2752dc720350/Untitled.png)

인덱스 패턴이 생성되면 Kibana의 Discovery 탭에서 실시간으로 들어오는 로그들을 확인 할 수 있다.

c. **슬랙 알람 설정**

**적재 성공 알람 설정**

스마트 스토어 쇼핑몰 별로 매일 정해진 시간에 수행되어야 하는 배치들이 있다. 이 배치들이 실행되어 브로커에 데이터가 적재되면 logstash 컨슈머에서 데이터를 받아와 opensearch에 적재하게 된다.

logstash를 통해 Opensearch에 정상적으로 수행되었는지 매일 확인하기 어렵기 때문에 알람을 설정해 두었다. Opendistro for elasticsearch의 Alert 기능을 사용하고, Crawler 파드가 스마트 스토어의 모든 리뷰를 성공적으로 가져왔다면 status 필드에 Success라는 메세지를 보내도록 설정해두어야 한다.

**Destination 설정**

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/6ae09152-d562-47c3-b037-768b81eb442d/Untitled.png)

먼저 메세지를 보낼 Destination을 설정한다. Name, Type, webhook url을 입력하여 생성한다.

**Monitor 설정**

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2915cea3-6ba7-4c52-b9f9-f077895d0b17/Untitled.png)

모니터 생성 화면에 들어가서 Monitor 이름을 입력한다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/fdf675c1-e33a-4ece-b3be-f724fd8c271b/Untitled.png)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/3709a3fc-ed2a-4faa-ba5b-5c84987d765b/Untitled.png)

Define Monitor 탭에서 Define using exraction query를 선택하고  조회할 index를 선택한 후, 어떤 쿼리로 조회할 지 입력한다.  이번 프로젝트에서는 현재 시간부터 2분 이내에 들어온 status 필드 값 중 Success 인 값을 조회하도록 설정했다. 조건을 설정한 쿼리는 다음과 같다.

**Opendisro-Alerting-Slack**

```yaml
{
    "size": 0,
    "query": {
        "bool": {
            "filter": [
                {
                    "range": {
                        "timestamp": {
                            "from": "{{period_end}}||+9h-2m",
                            "to": "{{period_end}}||+9h",
                            "include_lower": true,
                            "include_upper": true,
                            "format": "epoch_millis",
                            "boost": 1
                        }
                    }
                },
                {
                    "match": {
                        " status": {
                            "query": "Success",
                            "operator": "OR",
                            "prefix_length": 0,
                            "max_expansions": 50,
                            "fuzzy_transpositions": true,
                            "lenient": false,
                            "zero_terms_query": "NONE",
                            "auto_generate_synonyms_phrase_query": true,
                            "boost": 1
                        }
                    }
                }
            ],
            "adjust_pure_negative": true,
            "boost": 1
        }
    }
}
```

- range : 데이터가 조회될 범위를 설정할 수 있다. 현재 시간부터 2분 이내에 들어온 데이터를 조회하도록 설정했다. 여기서 중요한 점은 opensearch의 period_end는 UTC+0을 기준으로 설정되어 있다는 점이다.
    
    앞서 설정했던 KST Timestamp와 약 9시간의 차이가 있기 때문에 period_end에 9시간을 더해 시간 값을 조정한 후 2분의 범위를 설정했다.
    
- match : status 필드에 `Success` 라는 값을 조회하도록 설정했다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/95d02856-f60a-498f-acb9-466a80767b79/Untitled.png)

마지막으로 Monitor schedule을 설정하고 Monitor 설정을 마무리한다. `By interval`로 1분마다 조회하도록 설정했다.

**Trigger 설정**

Monitor 설정을 완료했다면, Trigger를 설정해야 한다. Trigger Name 을 입력하고 Trigger Condition 항목을 설정한다. 정해진 시간 범위 내에 적재 성공 메세지가 1개 이상 발생하면 알람을 받고 싶기 때문에 다음과 같이 설정한다.

```
ctx.results[0].hits.total.value > 0
```

마지막으로 trigger 생성 화면 제일 하단에 있는 Configure Action 부분을 설정한다. Action Name을 입력하고 아까 생성한 Destination 을 선택한다. 

Message 와 Message Preview 필드 중간에 있는 버튼을 눌러서 Slack으로 메시지가 오는지 확인 후 Trigger를 생성한다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2cdfad80-e756-4f02-8456-30c79d5d390b/Untitled.png)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/50a72edb-4b16-43b3-aa9b-121cba4d1dbb/Untitled.png)

슬랙 메세지에 적재 완료 시간과 로그를 확인할 수 있는 URL을 메세지로 설정한다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/8402e36b-3ad2-4afd-b4c8-832227a519fb/Untitled.png)

알람 메세지가 성공적으로 전송된 것을 확인할 수 있다.

d. 분석 데이터 인덱스 생성

Jupyter Notebook 에서 분석된 데이터로 시각화를 진행한다. 분석 데이터를 담을 인덱스를 생성한다.

```yaml
## 분석결과 인덱스 mapping 설정
PUT analyzed_data
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 3
  }, 
  "mappings": {
    "properties": {
      "Name" : {
        "type": "keyword"
      },
      "Star" : {
        "type": "long"
      },
      "Date" : {
        "type" : "date"
      },
      "Word" : {
        "type": "keyword"
      },
      "Sentiment" : {
        "type" : "keyword"
      },
      "Adjustment-sentiment" : {
        "type" : "keyword"
      }
    }
  }
}
```

- number_of_shards : 해당 인덱스의 프라이머리 샤드의 수를 지정한다.
- number_of_replicas : 해당 인덱스의 복제본 샤드의 수를 지정한다.
- properties : RDBMS의 schema에 해당하는 것으로 필드의 이름과 데이터 타입을 지정한다.
    - Name : 쇼핑몰의 이름
    - Star : 평점
    - Date : 리뷰 작성일
    - Word : 토큰화 된 리뷰 단어
    - Sentiment : 조정 전 감성분석 결과(긍정, 부정)
    - Adjustment-sentiment : 조정 후 감성분석 결과(긍정, 부정)
