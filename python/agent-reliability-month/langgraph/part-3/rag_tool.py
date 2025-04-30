import os
import time

from dotenv import load_dotenv
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from langchain_text_splitters import MarkdownHeaderTextSplitter
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Supply Chain Knowledge Base
SUPPLY_CHAIN_KNOWLEDGE = """## Supply Chain Fundamentals

Supply chain management encompasses the planning and management of all activities involved in sourcing, procurement, conversion, and logistics management activities. It includes coordination and collaboration with channel partners, suppliers, intermediaries, third-party service providers, and customers.

A typical supply chain consists of several key components: suppliers, manufacturers, distributors, retailers, and end customers. The flow of materials, information, and finances moves through these entities in both directions. Effective supply chain management requires visibility across all these components to optimize performance, reduce costs, and mitigate risks.

Key performance indicators (KPIs) for supply chains include cost efficiency, delivery performance, quality metrics, flexibility, and sustainability measures. Modern supply chains must balance efficiency with resilience, especially in light of recent global disruptions.

## Risk Management

Supply chain risk management involves identifying, assessing, and mitigating potential disruptions that could impact operations. Risks can be categorized into several types: operational risks (supplier failures, quality issues), financial risks (currency fluctuations, credit risks), strategic risks (competitive pressures, regulatory changes), and external risks (natural disasters, geopolitical events).

Risk assessment typically involves probability analysis and impact evaluation. High-probability, high-impact risks require immediate attention and robust mitigation strategies. Common mitigation approaches include supplier diversification, safety stock management, alternative sourcing strategies, and business continuity planning.

Supply chain resilience is built through redundancy, flexibility, and visibility. Organizations should develop multiple sourcing options, maintain strategic inventory buffers, and invest in real-time monitoring systems to detect and respond to disruptions quickly.

## Supplier Evaluation and Management

Supplier evaluation is a critical process that involves assessing potential and existing suppliers across multiple dimensions. Key evaluation criteria include quality capabilities, delivery performance, financial stability, technical competencies, and strategic alignment with organizational goals.

The supplier selection process typically includes Request for Information (RFI), Request for Proposal (RFP), and detailed supplier audits. Evaluation should consider total cost of ownership rather than just purchase price, including factors like transportation costs, inventory carrying costs, quality costs, and risk-related costs.

Ongoing supplier management involves performance monitoring, relationship development, and continuous improvement initiatives. Supplier scorecards track key metrics such as on-time delivery, quality ratings, cost performance, and responsiveness. Strategic suppliers often participate in joint improvement programs and innovation partnerships.

## Logistics and Transportation

Logistics encompasses the planning, implementation, and control of the movement and storage of goods, services, and information. Transportation is a critical component, representing a significant portion of total logistics costs for most organizations.

Transportation modes each have distinct characteristics: road transport offers flexibility and door-to-door service but higher costs per unit for long distances; rail transport provides cost-effective bulk transportation but limited accessibility; air transport enables fast delivery but at premium costs; ocean freight offers the lowest cost per unit for international shipments but longest transit times.

Logistics network design involves optimizing the number, location, and capacity of facilities such as distribution centers, warehouses, and cross-docking facilities. Factors to consider include customer proximity, transportation costs, labor availability, real estate costs, and regulatory requirements.

## Inventory Management

Inventory management balances the costs of holding inventory against the risks of stockouts. Key inventory types include raw materials, work-in-progress, and finished goods. Each requires different management approaches based on demand patterns, lead times, and value characteristics.

Classical inventory models include Economic Order Quantity (EOQ) for determining optimal order sizes, and reorder point systems for timing replenishment. Modern approaches leverage demand forecasting, vendor-managed inventory (VMI), and just-in-time (JIT) principles to minimize inventory while maintaining service levels.

ABC analysis categorizes inventory based on value contribution, allowing focused attention on high-value items. Safety stock calculations consider demand variability, lead time uncertainty, and desired service levels. Advanced inventory optimization uses statistical models and machine learning to improve forecast accuracy and inventory positioning.

## Technology in Supply Chain

Digital transformation is reshaping supply chain management through various technologies. Enterprise Resource Planning (ERP) systems provide integrated platforms for managing business processes across functions. Supply Chain Management (SCM) software offers specialized capabilities for planning, execution, and optimization.

Internet of Things (IoT) devices enable real-time tracking and monitoring of assets, shipments, and environmental conditions. Radio Frequency Identification (RFID) and GPS technologies provide visibility into inventory locations and movements. Sensors can monitor temperature, humidity, shock, and other parameters critical for sensitive products.

Artificial Intelligence and Machine Learning applications include demand forecasting, route optimization, predictive maintenance, and automated decision-making. Blockchain technology offers potential for improved traceability, authentication, and smart contract execution in supply chain transactions.

## Sustainability and ESG

Environmental, Social, and Governance (ESG) considerations are increasingly important in supply chain management. Environmental factors include carbon footprint reduction, waste minimization, water usage, and circular economy principles. Organizations are implementing green logistics practices, sustainable packaging, and renewable energy adoption.

Social responsibility encompasses labor practices, human rights, community impact, and ethical sourcing. Supplier codes of conduct address working conditions, fair wages, child labor prevention, and safety standards. Supply chain transparency initiatives improve visibility into social practices throughout the network.

Governance aspects include compliance management, risk oversight, and stakeholder engagement. Sustainable supply chain strategies often require investment in monitoring systems, supplier development programs, and alternative materials or processes.

## Compliance and Regulations

Supply chain compliance involves adherence to various laws, regulations, and standards across different jurisdictions. Key areas include trade regulations (customs, tariffs, free trade agreements), product safety standards, environmental regulations, and labor laws.

International trade compliance requires understanding of export controls, import regulations, and documentation requirements. Customs procedures, duty calculations, and preferential trade programs can significantly impact costs and transit times. Non-compliance can result in penalties, delays, and reputational damage.

Industry-specific regulations may apply to pharmaceuticals (FDA regulations), food products (HACCP, FDA Food Safety Modernization Act), automotive (safety standards), and chemicals (REACH, OSHA). Quality management systems like ISO 9001 provide frameworks for consistent quality assurance across the supply chain.

## Global Supply Chain Considerations

Global supply chains offer access to new markets, cost advantages, and specialized capabilities but introduce additional complexities. Currency fluctuations can significantly impact costs and profitability. Political risks include changes in trade policies, sanctions, and geopolitical tensions.

Cultural differences affect communication, business practices, and relationship management. Time zone differences can impact coordination and response times. Language barriers may lead to misunderstandings and errors in specifications or documentation.

Infrastructure variations across countries affect transportation options, reliability, and costs. Some regions may have limited port facilities, poor road networks, or unreliable power supplies. These factors must be considered in supply chain design and contingency planning."""


class SupplyChainRAG:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.retrieval_chain = None
        self.index_name = "supply-chain-rag"
        self._initialized = False

    def initialize(self):
        """Initialize the RAG system with supply chain knowledge"""
        if self._initialized:
            return

        try:
            # Initialize embeddings
            self.embeddings = PineconeEmbeddings(model='multilingual-e5-large')

            # Initialize Pinecone
            pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
            cloud = os.environ.get('PINECONE_CLOUD', 'aws')
            region = os.environ.get('PINECONE_REGION', 'us-east-1')
            spec = ServerlessSpec(cloud=cloud, region=region)

            # Create or use existing index
            if self.index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=self.index_name,
                    dimension=self.embeddings.dimension,
                    metric="cosine",
                    spec=spec
                )
                time.sleep(5)  # Wait for index to be ready

                # Split and load documents
                self._load_documents()
            else:
                # Connect to existing index
                self.vectorstore = PineconeVectorStore(
                    index_name=self.index_name,
                    embedding=self.embeddings,
                    namespace="supply-chain"
                )

            # Set up retrieval chain
            self._setup_retrieval_chain()
            self._initialized = True

            print("✅ Supply Chain RAG initialized successfully")

        except Exception as e:
            print(f"❌ Error initializing Supply Chain RAG: {e}")
            # Don't raise - allow the module to load and handle errors gracefully
            self._initialized = False

    def _load_documents(self):
        """Load and process supply chain documents"""
        # Split documents by headers
        headers_to_split_on = [("##", "Header 2")]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )

        doc_splits = markdown_splitter.split_text(SUPPLY_CHAIN_KNOWLEDGE)

        # Create vector store
        self.vectorstore = PineconeVectorStore.from_documents(
            documents=doc_splits,
            index_name=self.index_name,
            embedding=self.embeddings,
            namespace="supply-chain"
        )

        print(f"📚 Loaded {len(doc_splits)} supply chain document chunks")

    def _setup_retrieval_chain(self):
        """Set up the retrieval chain for Q&A"""
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

        llm = ChatOpenAI(temperature=0.0, model="gpt-4", name="Retriever- Supply Chain")

        combine_docs_chain = create_stuff_documents_chain(
            llm, retrieval_qa_chat_prompt
        )

        self.retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    def search(self, query: str) -> str:
        """Search the supply chain knowledge base"""
        # Lazy initialization - only initialize when first used
        if not self._initialized:
            self.initialize()

        if not self.retrieval_chain:
            return "RAG system not initialized. Please check your environment variables and try again."

        try:
            result = self.retrieval_chain.invoke({"input": query})
            return result['answer']
        except Exception as e:
            return f"Error during RAG search: {str(e)}"


# Global RAG instance - but don't initialize it yet
_supply_chain_rag = None


def get_rag_instance():
    """Get or create the global RAG instance"""
    global _supply_chain_rag
    if _supply_chain_rag is None:
        _supply_chain_rag = SupplyChainRAG()
    return _supply_chain_rag


@tool
def rag_search(query: str) -> str:
    """
    Search the supply chain knowledge base for information about supply chain management,
    risk management, supplier evaluation, logistics, inventory management, technology,
    sustainability, compliance, and global supply chain considerations.

    Args:
        query: The question or topic to search for in the supply chain knowledge base

    Returns:
        Relevant information from the supply chain knowledge base
    """
    rag_instance = get_rag_instance()
    return rag_instance.search(query)
