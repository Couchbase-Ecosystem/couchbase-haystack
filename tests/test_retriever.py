import os

from unittest.mock import MagicMock, Mock, patch
import pytest
from couchbase_haystack import CouchbaseDocumentStore
from couchbase_haystack import CouchbaseEmbeddingRetriever, CouchbaseDocumentStore
from couchbase_haystack import CouchbasePasswordAuthenticator

from haystack.dataclasses import Document
from haystack import GeneratedAnswer, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators import HuggingFaceAPIGenerator
import couchbase.search as search
from couchbase.search import SearchQuery


@pytest.mark.unit
class TestRetrieverUnit:
    @pytest.fixture
    def doc_store(self):
        yield MagicMock(spec=CouchbaseDocumentStore)

    def test_to_dict(self, doc_store: MagicMock):
        ac_doc_store = CouchbaseDocumentStore(
            authenticator=CouchbasePasswordAuthenticator(),
            bucket="haystack_integration_test",
            scope="haystack_test_scope",
            collection="haystack_collection",
            vector_search_index="vector_search",
        )
        doc_store.to_dict.return_value = ac_doc_store.to_dict()
        retriever = CouchbaseEmbeddingRetriever(document_store=doc_store, top_k=15)
        serialized_retriever = retriever.to_dict()
        # assert serialized_store["init_parameters"].pop("collection_name").startswith("test_collection_")
        assert serialized_retriever == {
            "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseEmbeddingRetriever",
            "init_parameters": {
                "top_k": 15,
                "document_store": {
                    "type": "couchbase_haystack.document_stores.document_store.CouchbaseDocumentStore",
                    "init_parameters": {
                        "cluster_connection_string": {"type": "env_var", "env_vars": ["CB_CONNECTION_STRING"], "strict": True},
                        "authenticator": {
                            "type": "couchbase_haystack.document_stores.auth.CouchbasePasswordAuthenticator",
                            "init_parameters": {
                                "username": {"type": "env_var", "env_vars": ["CB_USERNAME"], "strict": True},
                                "password": {"type": "env_var", "env_vars": ["CB_PASSWORD"], "strict": True},
                                "cert_path": None,
                            },
                        },
                        "cluster_options": {
                            "type": "couchbase_haystack.document_stores.cluster_options.CouchbaseClusterOptions",
                            "init_parameters": {},
                        },
                        "bucket": "haystack_integration_test",
                        "scope": "haystack_test_scope",
                        "collection": "haystack_collection",
                        "vector_search_index": "vector_search",
                    },
                },
            },
        }

    def test_from_dict(self):
        retriever = CouchbaseEmbeddingRetriever.from_dict(
            {
                "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseEmbeddingRetriever",
                "init_parameters": {
                    "top_k": 15,
                    "document_store": {
                        "type": "couchbase_haystack.document_stores.document_store.CouchbaseDocumentStore",
                        "init_parameters": {
                            "cluster_connection_string": {
                                "type": "env_var",
                                "env_vars": ["CB_CONNECTION_STRING"],
                                "strict": True,
                            },
                            "authenticator": {
                                "type": "couchbase_haystack.document_stores.auth.CouchbasePasswordAuthenticator",
                                "init_parameters": {
                                    "username": {"type": "env_var", "env_vars": ["CB_USERNAME"], "strict": True},
                                    "password": {"type": "env_var", "env_vars": ["CB_PASSWORD"], "strict": True},
                                    "cert_path": None,
                                },
                            },
                            "cluster_options": {
                                "type": "couchbase_haystack.document_stores.cluster_options.CouchbaseClusterOptions",
                                "init_parameters": {},
                            },
                            "bucket": "haystack_integration_test",
                            "scope": "haystack_test_scope",
                            "collection": "haystack_collection",
                            "vector_search_index": "vector_search",
                        },
                    },
                },
            }
        )
        assert retriever.top_k == 15
        assert isinstance(retriever.document_store.authenticator, CouchbasePasswordAuthenticator)
        assert retriever.document_store.bucket == "haystack_integration_test"
        assert retriever.document_store.scope_name == "haystack_test_scope"
        assert retriever.document_store.collection_name == "haystack_collection"
        assert retriever.document_store.vector_search_index == "vector_search"

    def test_run(self, doc_store: MagicMock):
        doc_store._embedding_retrieval.return_value = [Document(content="Who created the Dothraki vocabulary?")]
        retriever = CouchbaseEmbeddingRetriever(document_store=doc_store, top_k=15)
        rag_pipeline = Pipeline()
        rag_pipeline.add_component(
            "query_embedder",
            SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2", progress_bar=False),
        )
        rag_pipeline.add_component("retriever", retriever)
        rag_pipeline.connect("query_embedder", "retriever.query_embedding")

        # Ask a question on the data you just added.
        question = "Who created the Dothraki vocabulary?"
        sq = search.BooleanQuery(
            must=search.ConjunctionQuery(search.MatchQuery("term2", field="field1"), search.MatchQuery("term", field="field3"))
        )
        data = {
            "query_embedder": {"text": question},
            "retriever": {"top_k": 3, "search_query": sq},
        }
        result = rag_pipeline.run(data)
        doc_store._embedding_retrieval.assert_called_once_with(
            query_embedding=[
                -0.041543617844581604,
                0.007472909986972809,
                -0.05073462426662445,
                -0.019435549154877663,
                -0.07646062225103378,
                -0.09583791345357895,
                0.049671854823827744,
                0.004925557877868414,
                0.020372627303004265,
                0.05773279443383217,
                0.07020967453718185,
                -0.02308022789657116,
                -0.005538682918995619,
                0.03684994578361511,
                -0.026723191142082214,
                0.029128817841410637,
                -0.0314018689095974,
                0.016639621928334236,
                0.006701967213302851,
                -0.06519662588834763,
                0.07415109872817993,
                0.03666333109140396,
                0.05105183273553848,
                0.018955470994114876,
                0.12544474005699158,
                0.002733762376010418,
                -0.03704313561320305,
                0.006784259807318449,
                0.03943255543708801,
                0.02468833699822426,
                -0.03544219583272934,
                -0.007084422279149294,
                0.05268249288201332,
                0.009774517267942429,
                -0.01997547037899494,
                0.07490786164999008,
                0.05443975701928139,
                0.0964796394109726,
                0.0649881586432457,
                0.006276839878410101,
                -0.09811362624168396,
                0.02102266624569893,
                0.013945161364972591,
                0.0057843527756631374,
                0.03501288965344429,
                0.0578814297914505,
                -0.004882254172116518,
                0.025709304958581924,
                -0.006928971502929926,
                0.0877685397863388,
                -0.06228732690215111,
                -0.07691650092601776,
                -0.029270945116877556,
                -0.032746076583862305,
                -0.039360854774713516,
                -0.027540452778339386,
                -0.06302612274885178,
                0.0749661773443222,
                -0.02428562007844448,
                -0.008998241275548935,
                -0.0036097327247262,
                -0.024736635386943817,
                -0.07179892808198929,
                0.12422487884759903,
                -0.09709367156028748,
                -0.06946579366922379,
                0.005635398905724287,
                -0.004777474328875542,
                0.009085128083825111,
                0.04973355308175087,
                0.030185814946889877,
                0.03579006716609001,
                0.09256280213594437,
                -0.05162617191672325,
                -0.0391247384250164,
                -0.04354725778102875,
                0.0516752228140831,
                -0.08701856434345245,
                -0.03213489428162575,
                -0.07271404564380646,
                0.02087569050490856,
                0.0945790633559227,
                0.05668126791715622,
                0.07492095977067947,
                -0.08784355223178864,
                0.07479120790958405,
                0.004411892034113407,
                0.009358753450214863,
                -0.01958945021033287,
                -0.10895141959190369,
                0.05725044757127762,
                -0.0842810645699501,
                -0.017514903098344803,
                0.004569910932332277,
                -0.04596801474690437,
                -0.0077735730446875095,
                -0.030928222462534904,
                0.027823301032185555,
                0.01696341671049595,
                0.04731646552681923,
                -0.003686588956043124,
                -0.04747160151600838,
                -0.02903902716934681,
                -0.015755027532577515,
                -0.060731250792741776,
                -0.07014545798301697,
                -0.009117958135902882,
                -0.022124862298369408,
                0.04648139700293541,
                0.018427718430757523,
                -0.05834544077515602,
                0.0016277657123282552,
                0.01208566129207611,
                -0.008059544488787651,
                -0.021062372252345085,
                0.013747683726251125,
                -0.04691930487751961,
                0.016355544328689575,
                0.0946347787976265,
                0.02652263082563877,
                0.022113140672445297,
                0.05837097018957138,
                -0.01024390384554863,
                0.03246862441301346,
                -0.033819764852523804,
                0.02673231065273285,
                0.002778115449473262,
                -4.252565709160635e-33,
                0.08646638691425323,
                0.08914558589458466,
                0.002240339992567897,
                0.035684190690517426,
                -0.02631712332367897,
                -0.07051024585962296,
                0.07887344062328339,
                -0.0900450050830841,
                -0.09335336834192276,
                -0.05912727117538452,
                0.034113164991140366,
                0.01445794478058815,
                -0.07141999900341034,
                0.02704794891178608,
                0.007689010351896286,
                0.010130309499800205,
                -0.03785869479179382,
                -0.005063625983893871,
                -0.06444627791643143,
                0.010902157053351402,
                0.03670574724674225,
                0.08819594234228134,
                0.0006998131866566837,
                -0.03341822326183319,
                -0.03600635007023811,
                0.014722231775522232,
                0.03847165405750275,
                -0.011770833283662796,
                -0.01593383401632309,
                0.07201765477657318,
                -0.009118515066802502,
                -0.008375356905162334,
                -0.008661620318889618,
                0.043309230357408524,
                0.05869991332292557,
                -0.02941420115530491,
                -0.050611045211553574,
                -0.07136586308479309,
                0.0412808358669281,
                -0.04608375206589699,
                0.018540628254413605,
                0.029082240536808968,
                -0.02638690173625946,
                -0.004927518777549267,
                -0.021494349464774132,
                0.06697751581668854,
                -0.013318252749741077,
                0.06043057143688202,
                -0.05917365849018097,
                -0.005788751877844334,
                -0.030221687629818916,
                -0.010242098942399025,
                0.028116237372159958,
                -0.02944079600274563,
                0.011952891014516354,
                -0.04242366924881935,
                -0.05347369238734245,
                -0.04690682142972946,
                0.028041228652000427,
                0.07345261424779892,
                0.009082341566681862,
                0.015747420489788055,
                0.05135837197303772,
                0.06522219628095627,
                0.06668515503406525,
                -0.04103900492191315,
                -0.024891488254070282,
                -0.0018930111546069384,
                0.03197949379682541,
                -0.024433467537164688,
                -0.02113525941967964,
                0.04794119670987129,
                -0.11619216203689575,
                0.01689298264682293,
                -0.008610193617641926,
                -0.0012973841512575746,
                0.030415872111916542,
                -0.05906360596418381,
                -0.09625592082738876,
                0.008654601871967316,
                -0.07938650995492935,
                -0.14817947149276733,
                -0.03365619480609894,
                0.010133011266589165,
                -0.07983645796775818,
                0.032637275755405426,
                0.06206584721803665,
                -0.010595781728625298,
                0.06852821260690689,
                -0.003439322579652071,
                -0.06892966479063034,
                -0.023464905098080635,
                -0.007116460707038641,
                -0.07057463377714157,
                -0.14216811954975128,
                1.6752565087583523e-33,
                -0.0644429549574852,
                0.0030254751909524202,
                -0.04479468986392021,
                0.022824203595519066,
                -0.07659358531236649,
                0.014855854213237762,
                0.01431888248771429,
                0.03674912825226784,
                0.07968637347221375,
                0.013877389021217823,
                0.025638973340392113,
                -0.013431906700134277,
                0.00022061000345274806,
                0.03412418067455292,
                0.032784853130578995,
                -0.03756977990269661,
                0.042476966977119446,
                0.03130444139242172,
                0.04041026905179024,
                0.030876636505126953,
                0.008650415576994419,
                0.02144198678433895,
                -0.14772959053516388,
                -0.03316263481974602,
                0.03158211335539818,
                -0.007827257737517357,
                -0.039977893233299255,
                -0.016859902068972588,
                -0.09963589906692505,
                0.1208370178937912,
                0.0029096747748553753,
                -0.03149477392435074,
                0.0006516213179565966,
                0.038678597658872604,
                -0.03078189119696617,
                0.014782720245420933,
                0.0022576835472136736,
                -0.02961123362183571,
                0.003665574360638857,
                0.007598060183227062,
                0.02072777971625328,
                0.011901402845978737,
                -0.014296400360763073,
                -0.0015387162566184998,
                0.013148716650903225,
                0.005383229348808527,
                -0.06224202737212181,
                0.0846780315041542,
                0.041294846683740616,
                -0.044342949986457825,
                0.011962175369262695,
                0.004795174580067396,
                0.07942724227905273,
                -0.09266285598278046,
                0.0335044339299202,
                -0.02217361517250538,
                0.023675739765167236,
                -0.014397185295820236,
                -0.022335510700941086,
                -0.03571823239326477,
                -0.04948827996850014,
                -0.061801258474588394,
                -0.014087339863181114,
                0.023993592709302902,
                0.048671286553144455,
                0.08595933765172958,
                -0.09669455885887146,
                0.015257810242474079,
                0.05399603024125099,
                -0.06659740954637527,
                0.02455102652311325,
                -0.000973951886408031,
                -0.02333127148449421,
                -0.027650119736790657,
                -0.08465079963207245,
                -0.00502211507409811,
                -0.020055217668414116,
                -0.09266204386949539,
                -0.08631333708763123,
                -0.025267018005251884,
                -0.008536235429346561,
                -0.037963349372148514,
                0.058037564158439636,
                0.036720648407936096,
                0.014546693302690983,
                0.0016263016732409596,
                -0.0068435524590313435,
                0.045070309191942215,
                0.011009113863110542,
                0.02834557369351387,
                0.0505652129650116,
                0.007415481377393007,
                0.020337210968136787,
                0.0926450565457344,
                -0.01978340372443199,
                -1.5621013815803053e-08,
                -0.02158724144101143,
                0.06533323228359222,
                0.0070434631779789925,
                -0.01599625125527382,
                -0.036499589681625366,
                -0.02027260884642601,
                0.10071215778589249,
                0.021013792604207993,
                -0.04847397282719612,
                0.01883731037378311,
                0.03733791410923004,
                0.11370888352394104,
                0.05669882148504257,
                0.011695962399244308,
                0.04000720754265785,
                -0.009719688445329666,
                0.13052813708782196,
                0.09163796901702881,
                -0.01576772704720497,
                -0.02508002519607544,
                0.06204474717378616,
                -0.01953991875052452,
                0.014134446159005165,
                -0.03786652535200119,
                -0.044543489813804626,
                0.0528409369289875,
                -0.005699885543435812,
                -0.02503327466547489,
                0.04821285605430603,
                -0.07124342769384384,
                0.0007106039556674659,
                0.07650867849588394,
                -0.025037409737706184,
                -0.05792558938264847,
                -0.0220770463347435,
                0.08721209317445755,
                -0.16193020343780518,
                -0.016105523332953453,
                0.05591440945863724,
                -0.04835275188088417,
                0.028000984340906143,
                0.1143474280834198,
                0.0245541799813509,
                0.04110554978251457,
                0.058603592216968536,
                0.03164500743150711,
                0.019389182329177856,
                -0.09691878408193588,
                0.04260479286313057,
                -0.08175776898860931,
                0.011865165084600449,
                0.14542533457279205,
                0.06401452422142029,
                -0.013126864098012447,
                0.013400198891758919,
                -0.028375845402479172,
                -0.01579953543841839,
                -0.031311314553022385,
                -0.052194125950336456,
                -0.10781718790531158,
                0.08802737295627594,
                0.013113719411194324,
                0.09495744109153748,
                -0.0024531420785933733,
            ],
            top_k=3,
            search_query=data["retriever"]["search_query"],
            limit=None,
        )
        assert result["retriever"]["documents"] == doc_store._embedding_retrieval.return_value