# <center>인터넷 쇼핑몰 리뷰를 활용한 NLP 감성분석 파이프라인 프로젝트</center>

<br/>


<p align="center"><img src="https://github.com/seonwoojh/img-source/blob/main/img/%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C.png" width="650" height="600"></p>
<br/>


### **프로젝트 개요**

쇼핑몰 수익성 향상을 위해 플랫폼 운영자는 소비자 니즈 파악 및 구매 유도를 해야 한다. 동시에 제품 구매 유도에 실패한 수요가 낮은 제품에 대해 부정적 평가를 받은 요인을 파악하여 보완 할 필요가 있다. 하지만 쇼핑몰 플랫폼 운영자는 단시간에 많은 소비자 반응을 일일이 파악하기 힘들다. 

따라서 본 프로젝트에서는 머신 러닝을 통해 학습한 결과를 바탕으로 리뷰 감성 분석을 진행하여 타겟 키워드를 확인할 수 있는 대시보드를 생성함으로써 쇼핑몰 플랫폼 운영자가 직접 리뷰를 읽지 않아도 단시간에 상품에 대한 소비자 반응을 판단할 수 있도록 한다.

<br/>

### **프로젝트 일정**

![Untitled](https://github.com/seonwoojh/img-source/blob/main/img/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%20%EC%9D%BC%EC%A0%95.png)


<br/>

### 프로젝트 역할 분담

| 이름 | 직책 | 역할 |
| ----- | ----- | ----- |
| 도효주 | PM | 프로젝트 전체 일정 관리, 문서 작업 |
| 선우지훈 | 팀원 | 텍스트 데이터 정제 및 저장, 대시보드 구현, 인프라 구축(OpenSearch, Logstash, Kibana, Kafka) |
| 오승우 | 팀원 | 프로젝트 개요 기획, 대시보드 구현, 데이터 프레임 구축 |
| 전중석 | 팀원 | 데이터 크롤링 및 NLP 처리, 데이터 프레임 구축, 인프라 구축, 대시보드 구현 |

<br/>

### **Outputs**

[🙋‍ 프로젝트 보고서 확인하기](https://github.com/seonwoojh/Datapipeline_Project/blob/main/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%20%EC%B5%9C%EC%A2%85%20%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf)

[🙋‍ ppt 확인하기](https://github.com/seonwoojh/Datapipeline_Project/blob/main/%EC%9D%B8%ED%84%B0%EB%84%B7%20%EC%87%BC%ED%95%91%EB%AA%B0%20%EB%A6%AC%EB%B7%B0%EB%A5%BC%20%ED%99%9C%EC%9A%A9%ED%95%9C%20NLP%20%EA%B0%90%EC%84%B1%EB%B6%84%EC%84%9D%20%ED%8C%8C%EC%9D%B4%ED%94%84%EB%9D%BC%EC%9D%B8.pdf)

<br/>

### **서비스 플로우**


<p align="center"><img src="https://github.com/seonwoojh/img-source/blob/main/img/%EC%84%9C%EB%B9%84%EC%8A%A4%20%ED%94%8C%EB%A1%9C%EC%9A%B0.png"></p>

**쇼핑몰 댓글 분석 요청하기**

1. 사용자가 온라인 쇼핑몰 댓글 분석을 요청한다.
2. 엔지니어는 크롤러에게 사용자 쇼핑몰의 댓글 추출을 요청한다.
3. 크롤러는 사용자의 쇼핑몰에 접근한여 댓글, 별점, 작성일자를 추출한다.
4. 크롤러는 추출한 데이터를 카프카 브로커의 토픽에 저장한다.

**쇼핑몰 댓글 데이터 정제 및 저장하기**

1. 토픽에 저장된 데이터를 불러와 특수문자를 제거하고 JSON 포멧으로 변환한다.
2. 정제된 데이터를 인덱싱하여 데이터 적재 서버(OpenSearch)에 저장한다.

**쇼핑몰 댓글 NLP 처리**

1. GRU를 사용하여 자사·타사·유사 쇼핑 리뷰 감성 분류를 진행한다.
2. 데이터 적재 서버에 저장 된 데이터를 불러와 자연어 처리를 한다.
3. 처리 결과를 다시 데이터 적재 서버에 저장한다.

**시각화**

1. 저장 된 데이터의 인덱스를 기반으로 대시보드 형태로 시각화한다.
2. 사용자에게 해당 대시보드의 주소를 제공한다

<br/>

### **기능 플로우**


<p align="center"><img src="https://github.com/seonwoojh/img-source/blob/main/img/%EA%B8%B0%EB%8A%A5%ED%94%8C%EB%A1%9C%EC%9A%B0.png" width="700"></p>

<br/>

### **전체 프로젝트 구조**


<p align="center"><img src="https://github.com/seonwoojh/img-source/blob/main/img/%EC%A0%84%EC%B2%B4%20%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%20%EA%B5%AC%EC%A1%B0.png" width="700"></p>

<br/>

### **Kafka** **아키텍처 구성도**
<p align="center"><img src="https://github.com/seonwoojh/img-source/blob/main/img/kafka.png" width="650" height="450"></p>

* Kafka는 총 3개의 서버로 클러스터를 구성했다. Kafka의 토픽은 쇼핑몰 별로 생성하여 관리하도록 설정하고, 병렬 처리를 위해 3개의 파티션으로 구성했다.

* Replication Factor의 수를 3으로 설정하여 모든 브로커에 토픽의 메세지를 복제해 관리함으로써 내결함성을 확보할 수 있도록 구성했다.

<br/>

### **ELK** **아키텍처 구성도**

<p align="center"><img src="https://github.com/seonwoojh/img-source/blob/main/img/ELK.png" width="650" height="450"></p>


**Namespace**

EKS 클러스터 내에서 ELK 리소스들을 효율적으로 관리하기 위해 논리적 분리 단위인 `ELK` 네임 스페이스를 생성했다.  이후 생성되는 모든 리소스들은 `namespace` 단위로 구분된다.

<br/>

**OpenSearch**

저장은 OpenSearch가 담당한다. ELK 스택의 핵심은 OpenSearch이며, 이 저장소를 기반으로 동작한다.  OpenSearch는 루씬 기반의 검색 엔진이다

OpenSearch 클러스터에는 `마스터 노드` 3개와 `데이터 노드` 3개 , `인제스트 노드` 3개로 총 9개의 노드로 구성되어 있다. 

`마스터노드`와 `인제스트 노드`는 `Deployment` 방식으로 배포하여 `Pod`들을 관리하고,  데이터의 저장을 담당하는 `데이터 노드는` `StatefulSet` 방식으로 생성하여 클러스터가 삭제되어도 데이터를 영구 보존할 수 있도록 설계했다.

마지막으로 Service는 마스터 노드와 데이터 노드는 `ClusterIP` 형태의 서비스로 구성하여 노드 간 통신은 가능하되 외부에서 접근할 수 없도록 설정하고, 인제스트 노드의 Service를 `NodePort` 형태로 배포하여 해당 노드를 통해서만 외부에서 접근 가능하도록 설정했다.

<br/>

**Kibana**

Kibana를 통해 저장된 데이터를 `분석`하고 `시각화`한다. OpenSearch에 저장된 쇼핑몰 리뷰 데이터에 대한 `Index 패턴`을 생성하고 `대시보드`를 통해 시각화한다. 로드밸런서 타입의 서비스를 생성하여 외부에서 접근이 가능했고, 로드밸런서 주소의 80번 포트로 접근하면 Kibana 클러스터에 접근할 수 있도록 구성했다.

<br/>

**Logstash**

`Deployment` 방식으로 `Logstash Pod`를 배포하고 Nodeport 타입의 서비스로 배포하였다. 

Kafka input plugin을 이용하여 브로커에 적재된 쇼핑몰 데이터를 OpenSearch의 데이터 노드에 적재한다.

Logstash 파이프 라인 중 Filter 플러그인을 사용하여 정제하도록 구성했다.. Logstash를 통해 들어온 데이터는 `Message` 필드 안에 한번에 들어오게 된다.

메세지 필드만 저장해도 되지만 추후 원활한 Kibana를 이용한 시각화를 위해 로그를 구분하여 각각의 `필드를 재생성`하는 필터를 추가한다.
