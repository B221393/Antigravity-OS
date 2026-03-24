import { Link, useParams, Routes, Route } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import notesData from '../data/notesData'; // notesDataをインポート

// NoteDetail コンポーネント
function NoteDetail() {
  const { noteId } = useParams<{ noteId: string }>();
  const content = noteId ? notesData[noteId] : "ノートが選択されていません。";

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">{noteId ? noteId.replace(/_/g, ' ') : "Select a Note"}</h2>
      <div className="prose prose-invert max-w-none"> {/* Tailwind Typography pluginを想定 */}
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
    </div>
  );
}

function Notes() {
  const markdownNotes = [
    "2026-02-03_Accenture_Research",
    "2026-02-03_Capcom_Research",
    "2026-02-03_CognitiveBias_DeepKnowledge",
    "2026-02-03_Company_Research_INDEX",
    "2026-02-03_CyberAgent_Research",
    "2026-02-03_Daikin_Research",
    "2026-02-03_DAILY_REPORT",
    "2026-02-03_DeNA_Research",
    "2026-02-03_Denso_Research",
    "2026-02-03_DesignAgile_DeepKnowledge",
    "2026-02-03_FANUC_Research",
    "2026-02-03_freee_Research",
    "2026-02-03_Fujitsu_Research",
    "2026-02-03_GREE_Research",
    "2026-02-03_Hitachi_Research",
    "2026-02-03_IBM_Research",
    "2026-02-03_Kawasaki_Research",
    "2026-02-03_KDDI_Research",
    "2026-02-03_Keyence_Research",
    "2026-02-03_Kyocera_Research",
    "2026-02-03_Kyoto_School_AI",
    "2026-02-03_LiberalArts_DeepKnowledge",
    "2026-02-03_LINEYahoo_Research",
    "2026-02-03_Meitec_Research",
    "2026-02-03_Mercari_Research",
    "2026-02-03_MitsubishiElectric_Research",
    "2026-02-03_MIXI_Research",
    "2026-02-03_MoneyForward_Research",
    "2026-02-03_Murata_Research",
    "2026-02-03_NEC_Research",
    "2026-02-03_Nintendo_Research",
    "2026-02-03_NTTData_Research",
    "2026-02-03_Omron_Research",
    "2026-02-03_Panasonic_Research",
    "2026-02-03_Rakuten_Research",
    "2026-02-03_Recruit_Research",
    "2026-02-03_SmartHR_Research",
    "2026-02-03_SMC_Research",
    "2026-02-03_SoftBank_Research",
    "2026-02-03_Sony_Research",
    "2026-02-03_SquareEnix_Research",
    "2026-02-03_Terumo_Research",
    "2026-02-03_Toyota_Research",
    "2026-02-03_VSM_Trends_Report",
    "2026-02-03_Yaskawa_Research",
    "2026-02-04_Event_Photo_Log",
    "2026-02-04_Kiwix_Integration_Plan",
    "2026-02-04_KoeiTecmo_Research",
    "2026-02-04_Meitec_Core_Story_Draft",
    "2026-02-04_UI-TARS_Research",
    "EGO_Specification_Summary",
    "ES_DEEP_DIVE_Q",
    "KINKI_DX_RESEARCH",
    "Master_ES_Template_2027",
    "skill",
    "TACTICAL_REVIVAL_PLAN",
  ];

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-4">Markdown Notes</h1>
      <div className="flex">
        <ul className="w-1/3 pr-4 list-disc pl-5">
          {markdownNotes.map((note) => (
            <li key={note} className="mb-2">
              <Link to={note} className="text-blue-400 hover:underline">
                {note.replace(/_/g, ' ').replace('.md', '')} {/* 表示用に整形 */}
              </Link>
            </li>
          ))}
        </ul>
        <div className="flex-1 border-l border-gray-700 pl-4">
          <Routes>
            <Route path="/:noteId" element={<NoteDetail />} />
            <Route path="/" element={<p>ノートを選択してください。</p>} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default Notes;
