function Projects() {
  const rustProjects = [
    "analyze_transcript_rs",
    "analyze_universe_rs",
    "cleanup_universe_rs",
    "dt_cannon_rs",
    "launcher_rs",
    "racing_ai_rs",
    "racing_ai_rust",
    "shogi_engine_rs",
    "simulate_router_rs",
    "test_ollama_logic_rs",
    "vectis_catalog_generator_rs",
    "vectis_cortex_pro_rs",
    "vectis_pro_station_rs",
    "vectis_scan_check_rs",
    "vectis-station-rs",
  ];

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-4">Rust Projects</h1>
      <ul className="list-disc pl-5">
        {rustProjects.map((project) => (
          <li key={project} className="mb-2">
            <a href={`/projects/${project}`} className="text-blue-400 hover:underline">
              {project}
            </a>
          </li>
        ))}
      </ul>
      <p className="mt-4">Click on a project name to see more details (not yet implemented).</p>
    </div>
  );
}

export default Projects;