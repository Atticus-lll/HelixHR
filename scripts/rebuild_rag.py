import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.rag.vectorstore import reset_collection
from app.rag.document_loader import DocumentChunker, extract_text_from_content
from app.rag.embeddings import get_embedding_model
from app.config import settings
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings

PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "data", "chroma_db")

HANDBOOK = """员工手册 v2.3

第一章 入职指南

1.1 新员工入职流程
新员工入职第一天需前往人事部（行政楼302室）办理入职手续，需携带身份证原件、学历证书、体检报告及寸照两张。入职手续办理完成后，将由直属上级分配工位及工号，并开通企业邮箱和门禁权限。企业邮箱格式为：姓名全拼@company.com。门禁卡需在入职当天下班前到安保处领取。

1.2 试用期规定
所有新入职员工均需经过3个月的试用期。试用期内工资为转正工资的80%，按月发放。试用期结束后，由直属上级进行转正评估，评估通过后提交人事部办理转正手续。转正后享受全额工资及全部福利待遇。

第二章 考勤与休假制度

2.1 工作时间
公司实行标准工时制，周一至周五为工作日，周六周日休息。上午上班时间为9:00，下班时间为18:00，中午12:00至13:00为午休时间。研发部门实行弹性工作制，可在8:30至10:00之间灵活选择上班时间，但须每天工作满8小时。

2.2 请假类型及审批流程
事假：因私事请假需提前1天申请，3天以内由直属上级审批，3天以上需部门负责人审批。病假：因病请假需提供医院证明，2天以内可事后补办。带薪年假：入职满1年享5天带薪年假，满3年享10天，满5年享15天。婚假：法定婚假3天，晚婚增加10天。产假：顺产98天，剖腹产增加15天，陪产假15天。

2.3 加班规定
加班需提前填写加班申请单，经直属上级审批后方可计为有效加班。平日加班按工资的150%计发，休息日加班按200%计发，法定节假日加班按300%计发。每月加班时长不得超过36小时。

第三章 薪酬与福利

3.1 薪酬结构
员工薪酬由基本工资、岗位工资、绩效工资、补贴及奖金组成。基本工资按职级确定，岗位工资按岗位系数计算，绩效工资根据季度考核结果发放。技术岗位另设技术津贴，标准为初级工程师500元/月，中级1000元/月，高级2000元/月。

3.2 社会保险及公积金
公司按国家规定为全体正式员工缴纳五险一金。养老保险个人缴费比例为8%，医疗保险2%，失业保险0.5%，住房公积金缴费比例为12%。所有费用由公司代扣代缴，每月10日前完成缴纳。

3.3 年终奖金
年终奖金根据公司年度经营状况及个人绩效确定，发放时间为每年春节前。绩效评级A的员工年终奖为4个月基本工资，B级为3个月，C级为2个月，D级为1个月。试用期员工按实际工作时间比例折算。

第四章 职级晋升

4.1 职级体系
公司实行技术和管理双通道晋升体系。技术序列：初级工程师 → 中级工程师 → 高级工程师 → 技术专家 → 首席技术官。管理序列：专员 → 主管 → 经理 → 总监 → 副总裁。每半年进行一次职级评审，由人力资源部组织评审委员会进行评定。

4.2 晋升条件
申请晋升至下一职级需满足：在当前职级任职满2年，近两次绩效考核均在B级以上，提交晋升述职报告，并通过评审答辩。破格晋升需满足：连续两次绩效考核为A级，且获得至少两名高一职级人员的推荐。

第五章 培训与发展

5.1 内部培训
公司每月举办一次新员工入职培训，内容包括公司文化、规章制度、业务介绍等。技术部门每周五下午开展技术分享会，鼓励员工分享专业知识和项目经验。外部培训需提前申请，报销上限为每人每年5000元。

5.2 职业发展
公司鼓励员工参加与岗位相关的职业资格考试，通过后给予一次性奖励。PMP认证奖励3000元，软考高项奖励2000元，中级职称评审费用全额报销。每年提供一次免费体检，费用由公司承担。"""

def main():
    print("Step 1: Reset ChromaDB collection...")
    reset_collection()
    client = chromadb.PersistentClient(
        path=PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    try:
        client.delete_collection(name=settings.rag.collection_name)
    except Exception:
        pass
    collection = client.create_collection(
        name=settings.rag.collection_name,
        metadata={"description": "EEMS document knowledge base"},
    )
    print(f"  Collection '{collection.name}' ready.")

    print("Step 2: Load embedding model...")
    embed_model = get_embedding_model()
    print(f"  Model: {settings.rag.embedding_model}")

    print("Step 3: Chunk document...")
    chunker = DocumentChunker(
        chunk_size=settings.rag.chunk_size,
        chunk_overlap=settings.rag.chunk_overlap,
    )
    doc_content = extract_text_from_content(HANDBOOK, "Claude", "员工手册")
    chunks = chunker.chunk_text(doc_content)
    print(f"  Generated {len(chunks)} chunks:")
    for i, c in enumerate(chunks):
        preview = c[:40].replace("\n", " ")
        print(f"    [{i}] {preview}...")

    print("Step 4: Generate embeddings...")
    embeddings = embed_model.embed_texts(chunks)
    print(f"  Done. Embedding dim: {len(embeddings[0])}")

    print("Step 5: Store in ChromaDB...")
    import json, hashlib
    doc_id = hashlib.sha256(("员工手册:" + HANDBOOK[:200]).encode()).hexdigest()[:16]
    chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    now = datetime.now().isoformat()
    metadatas = [
        {
            "title": "员工手册",
            "source": "Claude",
            "tags": json.dumps(["员工手册", "制度"]),
            "created_at": now,
            "chunk_index": i,
            "document_id": doc_id,
        }
        for i in range(len(chunks))
    ]
    collection.add(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    print(f"  Stored {collection.count()} chunks in ChromaDB.")
    print("Done!")

if __name__ == "__main__":
    main()
