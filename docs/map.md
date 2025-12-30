# Repository Map: mind-mcp

*Generated: 2025-12-30 03:53*

- **Files:** 469
- **Directories:** 104
- **Total Size:** 5.0M
- **Doc Files:** 317
- **Code Files:** 142
- **Areas:** 13 (docs/ subfolders)
- **Modules:** 32 (subfolders in areas)
- **DOCS Links:** 69 (0.49 avg per code file)

- markdown: 317
- python: 133
- typescript: 9

```
├── cli/ (105.6K)
│   ├── commands/ (45.8K)
│   │   ├── agents.py (12.1K) →
│   │   ├── events.py (14.9K) →
│   │   ├── fix_embeddings.py (1.1K)
│   │   ├── init.py (4.7K)
│   │   ├── tasks.py (11.7K) →
│   │   ├── upgrade.py (790)
│   │   └── (..2 more files)
│   ├── helpers/ (57.9K)
│   │   ├── check_mind_status_in_directory.py (5.0K)
│   │   ├── copy_capabilities_to_target.py (1.7K)
│   │   ├── copy_ecosystem_templates_to_target.py (4.0K)
│   │   ├── create_ai_config_files_for_claude_agents_gemini.py (2.2K)
│   │   ├── create_database_config_yaml.py (1.9K)
│   │   ├── fix_embeddings_for_nodes_and_links.py (9.2K)
│   │   ├── generate_embeddings_for_graph_nodes.py (2.2K)
│   │   ├── inject_seed_yaml_to_graph.py (11.6K)
│   │   ├── setup_database_and_apply_schema.py (5.0K)
│   │   ├── validate_embedding_config_matches_stored.py (2.3K)
│   │   └── (..15 more files)
│   ├── __main__.py (1.9K)
│   └── (..2 more files)
├── connectome/ (67.0K)
│   ├── adapters/ (12.3K)
│   │   ├── local.ts (7.1K)
│   │   ├── remote.ts (4.9K)
│   │   └── (..1 more files)
│   ├── core/ (15.5K)
│   │   ├── types/ (15.1K)
│   │   │   ├── adapter.ts (6.1K)
│   │   │   ├── schema.ts (8.7K)
│   │   │   └── (..1 more files)
│   │   └── (..1 more files)
│   ├── lib/ (36.2K)
│   │   ├── event-model.ts (8.0K)
│   │   ├── index.ts (1.9K)
│   │   ├── runtime-engine.ts (9.3K)
│   │   ├── state-store.ts (11.0K)
│   │   └── system-manifest.ts (6.0K)
│   ├── README.md (2.5K)
│   └── (..1 more files)
├── docs/ (2.6M)
│   ├── agents/ (227.8K)
│   │   ├── narrator/ (112.3K)
│   │   │   ├── archive/ (20.5K)
│   │   │   │   └── SYNC_archive_2024-12.md (20.5K)
│   │   │   ├── ALGORITHM_Scene_Generation.md (10.8K)
│   │   │   ├── BEHAVIORS_Narrator.md (5.0K)
│   │   │   ├── HEALTH_Narrator.md (13.0K)
│   │   │   ├── IMPLEMENTATION_Narrator.md (10.5K)
│   │   │   ├── PATTERNS_Narrator.md (7.8K)
│   │   │   ├── SYNC_Narrator.md (11.4K)
│   │   │   ├── SYNC_Narrator_archive_2025-12.md (15.4K)
│   │   │   ├── TEMPLATE_Player_Notes.md (1.8K)
│   │   │   ├── TOOL_REFERENCE.md (3.2K)
│   │   │   ├── VALIDATION_Narrator.md (8.6K)
│   │   │   └── (..4 more files)
│   │   ├── world-runner/ (104.5K)
│   │   │   ├── archive/ (23.7K)
│   │   │   │   └── SYNC_archive_2024-12.md (23.7K)
│   │   │   ├── ALGORITHM_World_Runner.md (11.3K)
│   │   │   ├── BEHAVIORS_World_Runner.md (8.0K)
│   │   │   ├── HEALTH_World_Runner.md (13.3K)
│   │   │   ├── IMPLEMENTATION_World_Runner_Service_Architecture.md (8.4K)
│   │   │   ├── INPUT_REFERENCE.md (1.9K)
│   │   │   ├── PATTERNS_World_Runner.md (7.5K)
│   │   │   ├── SYNC_World_Runner.md (16.2K)
│   │   │   ├── TEST_World_Runner_Coverage.md (3.6K)
│   │   │   ├── TOOL_REFERENCE.md (3.7K)
│   │   │   ├── VALIDATION_World_Runner_Invariants.md (6.3K)
│   │   │   └── (..1 more files)
│   │   └── PATTERNS_Agent_System.md (11.0K)
│   ├── architecture/ (56.7K)
│   │   └── cybernetic_studio_architecture/ (56.7K)
│   │       ├── ALGORITHM_Cybernetic_Studio_Process_Flow.md (4.4K)
│   │       ├── BEHAVIORS_Cybernetic_Studio_System_Behaviors.md (7.4K)
│   │       ├── HEALTH_Cybernetic_Studio_Health_Checks.md (7.6K)
│   │       ├── IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md (8.4K)
│   │       ├── OBJECTIVES_Cybernetic_Studio_Architecture_Goals.md (799)
│   │       ├── PATTERNS_Cybernetic_Studio_Architecture.md (16.1K)
│   │       ├── SYNC_Cybernetic_Studio_Architecture_State.md (7.0K)
│   │       └── VALIDATION_Cybernetic_Studio_Architectural_Invariants.md (5.0K)
│   ├── cli/ (133.9K)
│   │   ├── archive/ (5.4K)
│   │   │   ├── SYNC_CLI_Development_State_archive_2025-12.md (581)
│   │   │   ├── SYNC_CLI_State_Archive_2025-12.md (4.3K)
│   │   │   └── (..1 more files)
│   │   ├── core/ (54.7K)
│   │   │   ├── ALGORITHM_mind_cli_core.md (6.7K)
│   │   │   ├── BEHAVIORS_mind_cli_core.md (9.7K)
│   │   │   ├── HEALTH_mind_cli_core.md (6.6K)
│   │   │   ├── IMPLEMENTATION_mind_cli_core.md (8.6K)
│   │   │   ├── OBJECTIVES_mind_cli_core.md (4.8K)
│   │   │   ├── PATTERNS_mind_cli_core.md (6.0K)
│   │   │   ├── SYNC_mind_cli_core.md (6.6K)
│   │   │   └── VALIDATION_mind_cli_core.md (5.7K)
│   │   ├── prompt/ (39.7K)
│   │   │   ├── ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md (4.4K)
│   │   │   ├── BEHAVIORS_Prompt_Command_Output_and_Flow.md (3.5K)
│   │   │   ├── HEALTH_Prompt_Runtime_Verification.md (6.8K)
│   │   │   ├── IMPLEMENTATION_Prompt_Code_Architecture.md (7.8K)
│   │   │   ├── PATTERNS_Prompt_Command_Workflow_Design.md (4.7K)
│   │   │   ├── SYNC_Prompt_Command_State.md (7.7K)
│   │   │   └── VALIDATION_Prompt_Bootstrap_Invariants.md (4.8K)
│   │   ├── symbols/ (10.2K)
│   │   │   ├── ALGORITHM_Symbol_Extraction.md (3.2K)
│   │   │   ├── IMPLEMENTATION_Symbol_Extraction.md (3.9K)
│   │   │   ├── PATTERNS_Symbol_Extraction.md (1.9K)
│   │   │   └── SYNC_Symbol_Extraction.md (1.2K)
│   │   ├── ALGORITHM_CLI_Command_Execution_Logic.md (4.7K)
│   │   ├── BEHAVIORS_CLI_Module_Command_Surface_Effects.md (769)
│   │   ├── HEALTH_CLI_Module_Verification.md (599)
│   │   ├── IMPLEMENTATION_CLI_Code_Architecture.md (13.4K)
│   │   ├── OBJECTIVES_Cli_Goals.md (691)
│   │   ├── PATTERNS_CLI_Module_Overview_And_Scope.md (1.0K)
│   │   ├── VALIDATION_CLI_Module_Invariants.md (731)
│   │   ├── modules.md (1.8K)
│   │   └── (..1 more files)
│   ├── concepts/ (93.0K)
│   │   ├── clustering/ (51.6K)
│   │   │   ├── ALGORITHM_Dense_Clustering.md (9.5K)
│   │   │   ├── BEHAVIORS_Dense_Clustering.md (3.7K)
│   │   │   ├── HEALTH_Dense_Clustering.md (4.9K)
│   │   │   ├── IMPLEMENTATION_Cluster_Metrics.md (9.3K)
│   │   │   ├── IMPLEMENTATION_Dense_Clustering.md (9.1K)
│   │   │   ├── OBJECTIVES_Dense_Clustering.md (2.6K)
│   │   │   ├── PATTERNS_Dense_Clustering.md (4.1K)
│   │   │   ├── SYNC_Dense_Clustering.md (3.4K)
│   │   │   └── VALIDATION_Dense_Clustering.md (4.9K)
│   │   ├── coverage/ (40.0K)
│   │   │   ├── ALGORITHM_Coverage_Validation.md (8.2K)
│   │   │   ├── BEHAVIORS_Coverage_Validation.md (4.6K)
│   │   │   ├── IMPLEMENTATION_Coverage_Validation.md (9.1K)
│   │   │   ├── OBJECTIVES_Coverage_Validation.md (2.5K)
│   │   │   ├── PATTERNS_Coverage_Validation.md (6.8K)
│   │   │   ├── SYNC_Coverage_Validation.md (3.9K)
│   │   │   └── VALIDATION_Coverage_Validation.md (5.0K)
│   │   └── tempo-controller/ (1.3K)
│   │       └── CONCEPT_Tempo_Controller.md (1.3K)
│   ├── core_utils/ (34.0K)
│   │   ├── ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md (3.9K)
│   │   ├── BEHAVIORS_Core_Utils_Helper_Effects.md (3.6K)
│   │   ├── HEALTH_Core_Utils_Verification.md (7.4K)
│   │   ├── IMPLEMENTATION_Core_Utils_Code_Architecture.md (8.4K)
│   │   ├── OBJECTIVES_Core_Utils_Goals.md (719)
│   │   ├── PATTERNS_Core_Utils_Functions.md (2.2K)
│   │   ├── SYNC_Core_Utils_State.md (4.3K)
│   │   └── VALIDATION_Core_Utils_Invariants.md (3.6K)
│   ├── engine/ (254.3K)
│   │   ├── membrane/ (32.7K)
│   │   │   ├── ALGORITHM_Membrane_Modulation.md (4.3K)
│   │   │   ├── BEHAVIORS_Membrane_Modulation.md (4.5K)
│   │   │   ├── HEALTH_Membrane_Modulation.md (2.8K)
│   │   │   ├── IMPLEMENTATION_Membrane_Modulation.md (2.5K)
│   │   │   ├── PATTERNS_Membrane_Modulation.md (5.1K)
│   │   │   ├── PATTERNS_Membrane_Scoping.md (7.0K)
│   │   │   ├── SYNC_Membrane_Modulation.md (3.2K)
│   │   │   └── VALIDATION_Membrane_Modulation.md (3.3K)
│   │   ├── models/ (48.1K)
│   │   │   ├── ALGORITHM_Models.md (6.3K)
│   │   │   ├── BEHAVIORS_Models.md (4.0K)
│   │   │   ├── HEALTH_Models.md (4.4K)
│   │   │   ├── IMPLEMENTATION_Models.md (11.0K)
│   │   │   ├── OBJECTIVES_Models.md (4.4K)
│   │   │   ├── PATTERNS_Models.md (7.1K)
│   │   │   ├── SYNC_Models.md (5.6K)
│   │   │   └── VALIDATION_Models.md (5.3K)
│   │   ├── moment-graph-engine/ (35.7K)
│   │   │   ├── validation/ (6.4K)
│   │   │   │   ├── player_dmz/ (2.4K)
│   │   │   │   │   └── VALIDATION_Player_DMZ.md (2.4K)
│   │   │   │   ├── simultaneity_contradiction/ (1.8K)
│   │   │   │   │   └── VALIDATION_Simultaneity_Contradiction.md (1.8K)
│   │   │   │   └── void_tension/ (2.3K)
│   │   │   │       └── VALIDATION_Void_Tension.md (2.3K)
│   │   │   ├── ALGORITHM_Click_Wait_Surfacing.md (3.1K)
│   │   │   ├── BEHAVIORS_Traversal_And_Surfacing.md (2.4K)
│   │   │   ├── IMPLEMENTATION_Moment_Graph_Runtime_Layout.md (2.4K)
│   │   │   ├── OBJECTIVES_Moment_Graph_Engine.md (4.6K)
│   │   │   ├── PATTERNS_Instant_Traversal_Moment_Graph.md (3.7K)
│   │   │   ├── SYNC_Moment_Graph_Engine.md (2.9K)
│   │   │   ├── SYNC_Moment_Graph_Engine_archive_2025-12.md (6.1K)
│   │   │   ├── TEST_Moment_Graph_Runtime_Coverage.md (1.8K)
│   │   │   └── VALIDATION_Moment_Traversal_Invariants.md (2.2K)
│   │   ├── moments/ (16.4K)
│   │   │   ├── ALGORITHM_Moment_Graph_Operations.md (1.3K)
│   │   │   ├── BEHAVIORS_Moment_Lifecycle.md (1.4K)
│   │   │   ├── IMPLEMENTATION_Moment_Graph_Stub.md (870)
│   │   │   ├── OBJECTIVES_Moments.md (4.5K)
│   │   │   ├── PATTERNS_Moments.md (3.7K)
│   │   │   ├── SYNC_Moments.md (2.1K)
│   │   │   ├── TEST_Moment_Graph_Coverage.md (1.3K)
│   │   │   └── VALIDATION_Moment_Graph_Invariants.md (1.1K)
│   │   ├── self-improvement/ (115.1K)
│   │   │   ├── ALGORITHM_SelfImprovement.md (24.0K)
│   │   │   ├── BEHAVIORS_SelfImprovement.md (8.8K)
│   │   │   ├── HEALTH_SelfImprovement.md (18.0K)
│   │   │   ├── IMPLEMENTATION_SelfImprovement.md (23.3K)
│   │   │   ├── OBJECTIVES_SelfImprovement.md (6.6K)
│   │   │   ├── PATTERNS_SelfImprovement.md (12.0K)
│   │   │   ├── SYNC_SelfImprovement.md (4.7K)
│   │   │   ├── SYNC_SelfImprovement_archive_2025-12.md (4.3K)
│   │   │   └── VALIDATION_SelfImprovement.md (13.3K)
│   │   ├── ALGORITHM_Engine.md (687)
│   │   ├── BEHAVIORS_Engine.md (865)
│   │   ├── HEALTH_Engine.md (515)
│   │   ├── IMPLEMENTATION_Engine.md (852)
│   │   ├── OBJECTIVES_Engine_Goals.md (703)
│   │   ├── PATTERNS_Engine.md (1.1K)
│   │   ├── SYNC_Engine.md (798)
│   │   └── VALIDATION_Engine.md (666)
│   ├── infrastructure/ (219.2K)
│   │   ├── api/ (70.2K)
│   │   │   ├── ALGORITHM_Api.md (19.9K)
│   │   │   ├── ALGORITHM_Player_Input_Flow.md (7.3K)
│   │   │   ├── API_Graph_Management.md (4.3K)
│   │   │   ├── BEHAVIORS_Api.md (2.2K)
│   │   │   ├── HEALTH_Api.md (3.7K)
│   │   │   ├── IMPLEMENTATION_Api.md (7.8K)
│   │   │   ├── PATTERNS_Api.md (3.1K)
│   │   │   ├── SYNC_Api.md (4.0K)
│   │   │   ├── SYNC_Api_archive_2025-12.md (13.9K)
│   │   │   ├── VALIDATION_Api.md (2.4K)
│   │   │   └── (..2 more files)
│   │   ├── database-adapter/ (59.1K)
│   │   │   ├── ALGORITHM_DatabaseAdapter.md (6.3K)
│   │   │   ├── BEHAVIORS_DatabaseAdapter.md (4.2K)
│   │   │   ├── HEALTH_DatabaseAdapter.md (4.4K)
│   │   │   ├── IMPLEMENTATION_DatabaseAdapter.md (8.8K)
│   │   │   ├── OBJECTIVES_DatabaseAdapter.md (4.5K)
│   │   │   ├── PATTERNS_DatabaseAdapter.md (6.0K)
│   │   │   ├── PATTERNS_Database_Adapter.md (9.9K)
│   │   │   ├── SYNC_DatabaseAdapter.md (4.4K)
│   │   │   ├── SYNC_Database_Adapter.md (5.3K)
│   │   │   └── VALIDATION_DatabaseAdapter.md (5.5K)
│   │   ├── scene-memory/ (57.2K)
│   │   │   ├── archive/ (2.5K)
│   │   │   │   └── SYNC_archive_2024-12.md (2.5K)
│   │   │   ├── ALGORITHM_Scene_Memory.md (8.6K)
│   │   │   ├── BEHAVIORS_Scene_Memory.md (5.0K)
│   │   │   ├── HEALTH_Scene_Memory.md (518)
│   │   │   ├── IMPLEMENTATION_Scene_Memory.md (5.5K)
│   │   │   ├── OBJECTIVES_Scene_Memory_Goals.md (727)
│   │   │   ├── PATTERNS_Scene_Memory.md (4.7K)
│   │   │   ├── SYNC_Scene_Memory.md (6.0K)
│   │   │   ├── SYNC_Scene_Memory_archive_2025-12.md (15.3K)
│   │   │   ├── TEST_Scene_Memory.md (3.3K)
│   │   │   └── VALIDATION_Scene_Memory.md (5.1K)
│   │   ├── sse/ (438)
│   │   │   └── (..1 more files)
│   │   ├── tempo/ (29.0K)
│   │   │   ├── ALGORITHM_Tempo_Controller.md (3.1K)
│   │   │   ├── BEHAVIORS_Tempo.md (3.0K)
│   │   │   ├── HEALTH_Tempo.md (4.9K)
│   │   │   ├── IMPLEMENTATION_Tempo.md (7.3K)
│   │   │   ├── OBJECTIVES_Tempo_Goals.md (699)
│   │   │   ├── PATTERNS_Tempo.md (3.6K)
│   │   │   ├── SYNC_Tempo.md (4.0K)
│   │   │   └── VALIDATION_Tempo.md (2.6K)
│   │   └── wsl-autostart.md (3.2K)
│   ├── llm_agents/ (79.9K)
│   │   ├── ALGORITHM_Gemini_Stream_Flow.md (5.7K)
│   │   ├── BEHAVIORS_Gemini_Agent_Output.md (5.8K)
│   │   ├── HEALTH_LLM_Agent_Coverage.md (13.8K)
│   │   ├── IMPLEMENTATION_LLM_Agent_Code_Architecture.md (16.1K)
│   │   ├── OBJECTIVES_Llm_Agents_Goals.md (719)
│   │   ├── PATTERNS_Provider_Specific_LLM_Subprocesses.md (5.3K)
│   │   ├── SYNC_LLM_Agents_State.md (3.6K)
│   │   ├── SYNC_LLM_Agents_State_archive_2025-12.md (20.8K)
│   │   └── VALIDATION_Gemini_Agent_Invariants.md (8.1K)
│   ├── mcp-design/ (114.0K)
│   │   ├── ALGORITHM/ (2.4K)
│   │   │   └── ALGORITHM_Protocol_Process_Flow.md (2.4K)
│   │   ├── IMPLEMENTATION/ (5.5K)
│   │   │   └── IMPLEMENTATION_Protocol_File_Structure.md (5.5K)
│   │   ├── doctor/ (58.5K)
│   │   │   ├── ALGORITHM_Project_Health_Doctor.md (20.2K)
│   │   │   ├── BEHAVIORS_Project_Health_Doctor.md (9.3K)
│   │   │   ├── HEALTH_Project_Health_Doctor.md (5.2K)
│   │   │   ├── IMPLEMENTATION_Project_Health_Doctor.md (5.7K)
│   │   │   ├── PATTERNS_Project_Health_Doctor.md (4.0K)
│   │   │   ├── SYNC_Project_Health_Doctor.md (5.1K)
│   │   │   ├── SYNC_Project_Health_Doctor_archive_2025-12.md (3.9K)
│   │   │   └── VALIDATION_Project_Health_Doctor.md (5.2K)
│   │   ├── features/ (10.5K)
│   │   │   ├── BEHAVIORS_Agent_Trace_Logging.md (3.7K)
│   │   │   ├── PATTERNS_Agent_Trace_Logging.md (3.6K)
│   │   │   └── SYNC_Agent_Trace_Logging.md (3.2K)
│   │   ├── ALGORITHM_Protocol_Core_Mechanics.md (570)
│   │   ├── BEHAVIORS_Observable_Protocol_Effects.md (7.2K)
│   │   ├── HEALTH_Protocol_Verification.md (5.6K)
│   │   ├── IMPLEMENTATION_Protocol_System_Architecture.md (700)
│   │   ├── OBJECTIVES_Protocol_Goals.md (711)
│   │   ├── PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md (6.2K)
│   │   ├── SYNC_Protocol_Current_State.md (8.0K)
│   │   ├── SYNC_Protocol_Current_State_archive_2025-12.md (1.9K)
│   │   └── VALIDATION_Protocol_Invariants.md (6.1K)
│   ├── mcp-tools/ (94.5K)
│   │   ├── ALGORITHM_MCP_Tools.md (5.5K)
│   │   ├── BEHAVIORS_MCP_Tools.md (5.3K)
│   │   ├── HEALTH_MCP_Tools.md (11.9K)
│   │   ├── IMPLEMENTATION_MCP_Tools.md (6.2K)
│   │   ├── MAPPING_Doctor_Issues_To_Protocols.md (5.8K)
│   │   ├── MAPPING_Issue_Type_Verification.md (16.1K)
│   │   ├── SKILLS_AND_PROTOCOLS_Mapping.md (10.1K)
│   │   ├── SYNC_MCP_Tools_archive_2025-12.md (9.6K)
│   │   ├── VALIDATION_Completion_Verification.md (11.6K)
│   │   ├── VALIDATION_MCP_Tools.md (5.5K)
│   │   └── (..3 more files)
│   ├── physics/ (697.8K)
│   │   ├── VALIDATION_Physics/ (20.8K)
│   │   │   ├── VALIDATION_Physics_Invariants.md (18.4K)
│   │   │   └── VALIDATION_Physics_Procedures.md (2.4K)
│   │   ├── algorithms/ (126.9K)
│   │   │   ├── ALGORITHM_Physics_Energy_Flow_Sources_Sinks_And_Moment_Dynamics.md (985)
│   │   │   ├── ALGORITHM_Physics_Energy_Mechanics_And_Link_Semantics.md (102.5K)
│   │   │   ├── ALGORITHM_Physics_Handler_And_Input_Processing_Flows.md (915)
│   │   │   ├── ALGORITHM_Physics_Mechanisms.md (1.4K)
│   │   │   ├── ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md (19.3K)
│   │   │   ├── ALGORITHM_Physics_Speed_Control_And_Display_Filtering.md (898)
│   │   │   └── ALGORITHM_Physics_Tick_Cycle_Gating_Flips_And_Dispatch.md (932)
│   │   ├── archive/ (24.6K)
│   │   │   ├── IMPLEMENTATION_Physics_archive_2025-12.md (1.9K)
│   │   │   ├── SYNC_Physics_History_2025-12.md (4.5K)
│   │   │   ├── SYNC_Physics_archive_2025-12.md (17.9K)
│   │   │   └── (..1 more files)
│   │   ├── attention/ (26.7K)
│   │   │   ├── ALGORITHM_Attention_Energy_Split.md (1.3K)
│   │   │   ├── BEHAVIORS_Attention_Split_And_Interrupts.md (3.9K)
│   │   │   ├── IMPLEMENTATION_Attention_Energy_Split.md (1.1K)
│   │   │   ├── OBJECTIVES_Attention_Energy_Split.md (4.6K)
│   │   │   ├── PATTERNS_Attention_Energy_Split.md (6.1K)
│   │   │   ├── SYNC_Attention_Energy_Split.md (1.0K)
│   │   │   ├── VALIDATION_Attention_Split_And_Interrupts.md (8.2K)
│   │   │   └── (..1 more files)
│   │   ├── cluster-presentation/ (27.3K)
│   │   │   ├── ALGORITHM_Cluster_Presentation.md (15.5K)
│   │   │   ├── IMPLEMENTATION_Cluster_Presentation.md (7.7K)
│   │   │   └── PATTERNS_Cluster_Presentation.md (4.1K)
│   │   ├── graph/ (123.6K)
│   │   │   ├── archive/ (17.7K)
│   │   │   │   └── ALGORITHM_Energy_Flow_archived_2025-12-20.md (17.7K)
│   │   │   ├── BEHAVIORS_Graph.md (9.6K)
│   │   │   ├── OBJECTIVES_Graph.md (4.7K)
│   │   │   ├── PATTERNS_Graph.md (4.9K)
│   │   │   ├── SYNC_Graph.md (8.6K)
│   │   │   ├── SYNC_Graph_archive_2025-12.md (33.8K)
│   │   │   └── VALIDATION_Living_Graph.md (44.2K)
│   │   ├── mechanisms/ (16.9K)
│   │   │   ├── MECHANISMS_Attention_Energy_Split.md (4.3K)
│   │   │   ├── MECHANISMS_Awareness_Depth_Breadth.md (7.9K)
│   │   │   ├── MECHANISMS_Contradiction_Pressure.md (2.5K)
│   │   │   └── MECHANISMS_Primes_Lag_Decay.md (2.2K)
│   │   ├── nature/ (35.6K)
│   │   │   ├── ALGORITHM_Nature.md (4.9K)
│   │   │   ├── BEHAVIORS_Nature.md (3.2K)
│   │   │   ├── HEALTH_Nature.md (4.5K)
│   │   │   ├── IMPLEMENTATION_Nature.md (5.8K)
│   │   │   ├── OBJECTIVES_Nature.md (2.7K)
│   │   │   ├── PATTERNS_Nature.md (4.2K)
│   │   │   ├── SYNC_Nature.md (2.8K)
│   │   │   ├── SYNC_Nature_archive_2025-12.md (3.1K)
│   │   │   └── VALIDATION_Nature.md (4.4K)
│   │   ├── subentity/ (95.5K)
│   │   │   ├── ALGORITHM_SubEntity.md (15.9K)
│   │   │   ├── BEHAVIORS_SubEntity.md (7.6K)
│   │   │   ├── HEALTH_SubEntity.md (19.0K)
│   │   │   ├── IMPLEMENTATION_SubEntity.md (11.6K)
│   │   │   ├── OBJECTIVES_SubEntity.md (4.7K)
│   │   │   ├── PATTERNS_SubEntity.md (7.4K)
│   │   │   ├── SYNC_SubEntity.md (4.5K)
│   │   │   ├── SYNC_SubEntity_archive_2025-12.md (9.4K)
│   │   │   └── VALIDATION_SubEntity.md (15.4K)
│   │   ├── tick-runner/ (5.6K)
│   │   │   └── PATTERNS_Tick_Runner.md (5.6K)
│   │   ├── traversal_logger/ (13.5K)
│   │   │   ├── IMPLEMENTATION_Traversal_Logger.md (10.5K)
│   │   │   └── SYNC_Traversal_Logger.md (3.0K)
│   │   ├── ALGORITHM_Physics.md (18.6K)
│   │   ├── API_Physics.md (6.9K)
│   │   ├── DESIGN_Traversal_Logger.md (12.4K)
│   │   ├── EXAMPLE_Traversal_Log.md (15.7K)
│   │   ├── HEALTH_Energy_Physics.md (29.2K)
│   │   ├── HEALTH_Physics.md (12.3K)
│   │   ├── IMPLEMENTATION_Physics.md (38.1K)
│   │   ├── PATTERNS_Physics.md (15.2K)
│   │   ├── SYNC_Physics_archive_2025-12.md (11.2K)
│   │   ├── VALIDATION_Energy_Physics.md (15.4K)
│   │   └── (..4 more files)
│   ├── procedure/ (75.0K)
│   │   ├── ALGORITHM_Procedure.md (9.7K)
│   │   ├── BEHAVIORS_Procedure.md (7.0K)
│   │   ├── HEALTH_Procedure.md (12.7K)
│   │   ├── IMPLEMENTATION_Procedure.md (14.9K)
│   │   ├── OBJECTIVES_Procedure.md (3.3K)
│   │   ├── PATTERNS_Procedure.md (7.2K)
│   │   ├── SYNC_Procedure.md (3.6K)
│   │   ├── SYNC_Procedure_archive_2025-12.md (3.9K)
│   │   ├── VALIDATION_Procedure.md (6.0K)
│   │   └── VOCABULARY_Procedure.md (6.7K)
│   ├── schema/ (148.4K)
│   │   ├── ALGORITHM_Schema.md (11.3K)
│   │   ├── BEHAVIORS_Schema.md (7.7K)
│   │   ├── GRAMMAR_Link_Synthesis.md (53.4K)
│   │   ├── HEALTH_Schema.md (14.1K)
│   │   ├── IMPLEMENTATION_Schema.md (10.1K)
│   │   ├── OBJECTIVES_Schema.md (2.8K)
│   │   ├── PATTERNS_Schema.md (7.3K)
│   │   ├── SYNC_Schema.md (6.7K)
│   │   ├── SYNC_Schema_archive_2025-12.md (15.4K)
│   │   ├── VALIDATION_Schema.md (16.0K)
│   │   └── (..6 more files)
│   ├── tools/ (57.6K)
│   │   ├── ALGORITHM_Tools.md (6.7K)
│   │   ├── BEHAVIORS_Tools.md (4.8K)
│   │   ├── HEALTH_Tools.md (10.7K)
│   │   ├── IMPLEMENTATION_Tools.md (7.4K)
│   │   ├── OBJECTIVES_Tools_Goals.md (699)
│   │   ├── PATTERNS_Tools.md (5.9K)
│   │   ├── SYNC_Tools.md (16.3K)
│   │   └── VALIDATION_Tools.md (5.1K)
│   ├── ARCHITECTURE.md (4.4K)
│   └── map.md (286.7K)
├── engine/ (105.6K)
│   └── data/ (105.6K)
│       └── logs/ (105.6K)
│           └── traversal/ (105.6K)
│               ├── traversal_exp_0f9844ef.jsonl (2.5K)
│               ├── traversal_exp_0f9844ef.txt (2.1K)
│               ├── traversal_exp_532cb1fd.jsonl (26.9K)
│               ├── traversal_exp_532cb1fd.txt (9.9K)
│               ├── traversal_exp_9eee82be.jsonl (13.9K)
│               ├── traversal_exp_9eee82be.txt (5.7K)
│               ├── traversal_exp_a26866c1.jsonl (31.3K)
│               └── traversal_exp_a26866c1.txt (13.2K)
├── mcp/ (75.4K)
│   ├── tools/
│   │   └── (..1 more files)
│   ├── server.py (75.4K)
│   └── (..2 more files)
├── runtime/ (2.1M)
│   ├── actors/
│   │   └── (..4 more files)
│   ├── agents/ (127.2K)
│   │   ├── __init__.py (2.5K) →
│   │   ├── cli.py (3.2K) →
│   │   ├── graph.py (35.9K)
│   │   ├── liveness.py (11.5K)
│   │   ├── mapping.py (6.5K) →
│   │   ├── prompts.py (7.9K) →
│   │   ├── run.py (22.8K) →
│   │   └── verification.py (36.8K) →
│   ├── client/
│   │   └── (..5 more files)
│   ├── connectome/ (103.7K)
│   │   ├── __init__.py (734) →
│   │   ├── loader.py (4.8K) →
│   │   ├── persistence.py (11.3K) →
│   │   ├── runner.py (13.3K) →
│   │   ├── schema.py (16.3K) →
│   │   ├── session.py (7.1K) →
│   │   ├── steps.py (36.3K) →
│   │   ├── templates.py (7.6K)
│   │   └── validation.py (6.3K)
│   ├── graph/ (99.0K)
│   │   ├── adapter/ (21.3K)
│   │   │   ├── base.py (3.3K) →
│   │   │   ├── factory.py (5.6K) →
│   │   │   ├── falkordb.py (6.6K) →
│   │   │   ├── neo4j.py (5.7K) →
│   │   │   └── (..1 more files)
│   │   ├── ops/ (77.7K)
│   │   │   ├── links.py (23.2K)
│   │   │   ├── nodes.py (26.5K)
│   │   │   ├── queries.py (28.0K)
│   │   │   └── (..1 more files)
│   │   └── (..1 more files)
│   ├── infrastructure/ (243.4K)
│   │   ├── api/ (94.5K)
│   │   │   ├── app.py (28.1K) →
│   │   │   ├── graphs.py (14.9K)
│   │   │   ├── moments.py (17.7K)
│   │   │   ├── playthroughs.py (24.2K) →
│   │   │   ├── sse_broadcast.py (2.8K) →
│   │   │   ├── tempo.py (6.7K) →
│   │   │   └── (..1 more files)
│   │   ├── canon/ (30.9K)
│   │   │   ├── canon_holder.py (30.8K)
│   │   │   └── (..1 more files)
│   │   ├── database/ (23.5K)
│   │   │   ├── __init__.py (1.3K)
│   │   │   ├── adapter.py (3.3K) →
│   │   │   ├── factory.py (6.5K) →
│   │   │   ├── falkordb_adapter.py (6.6K) →
│   │   │   └── neo4j_adapter.py (5.7K) →
│   │   ├── embeddings/ (20.5K)
│   │   │   ├── __init__.py (1.9K) →
│   │   │   ├── embed_pending.py (2.9K)
│   │   │   ├── factory.py (4.1K) →
│   │   │   ├── openai_adapter.py (4.4K) →
│   │   │   └── service.py (7.2K) →
│   │   ├── memory/ (19.7K)
│   │   │   ├── moment_processor.py (19.5K) →
│   │   │   └── (..1 more files)
│   │   ├── orchestration/ (50.1K)
│   │   │   ├── __init__.py (506)
│   │   │   ├── agent_cli.py (7.0K)
│   │   │   ├── narrator.py (6.9K) →
│   │   │   ├── orchestrator.py (19.9K)
│   │   │   └── world_runner.py (15.9K) →
│   │   └── tempo/ (4.2K)
│   │       ├── tempo_controller.py (4.1K)
│   │       └── (..1 more files)
│   ├── ingest/ (73.6K)
│   │   ├── actors.py (4.4K) →
│   │   ├── capabilities.py (11.8K) →
│   │   ├── docs.py (36.9K)
│   │   ├── files.py (20.1K) →
│   │   └── (..1 more files)
│   ├── membrane/ (15.8K)
│   │   ├── __init__.py (893)
│   │   ├── broadcast.py (5.8K)
│   │   ├── client.py (4.3K)
│   │   ├── stimulus.py (4.4K)
│   │   └── (..2 more files)
│   ├── models/ (46.6K)
│   │   ├── __init__.py (2.6K) →
│   │   ├── base.py (12.6K)
│   │   ├── links.py (12.9K)
│   │   └── nodes.py (18.5K)
│   ├── physics/ (794.6K)
│   │   ├── archive/ (36.9K)
│   │   │   └── tick_v1_0.py (36.9K) →
│   │   ├── graph/ (233.7K)
│   │   │   ├── graph_ops.py (26.5K)
│   │   │   ├── graph_ops_apply.py (34.5K)
│   │   │   ├── graph_ops_links.py (23.2K)
│   │   │   ├── graph_ops_moments.py (20.0K)
│   │   │   ├── graph_ops_read_only_interface.py (8.8K) →
│   │   │   ├── graph_queries.py (28.0K)
│   │   │   ├── graph_queries_moments.py (19.5K) →
│   │   │   ├── graph_queries_search.py (31.3K) →
│   │   │   ├── graph_query_utils.py (14.8K) →
│   │   │   ├── graph_schema_cleanup.py (9.5K)
│   │   │   └── (..6 more files)
│   │   ├── health/ (100.1K)
│   │   │   ├── checkers/ (43.6K)
│   │   │   │   ├── __init__.py (1.2K) →
│   │   │   │   ├── energy_conservation.py (5.8K) →
│   │   │   │   ├── link_state.py (3.8K) →
│   │   │   │   ├── moment_lifecycle.py (4.3K) →
│   │   │   │   ├── no_negative.py (3.2K) →
│   │   │   │   ├── subentity.py (20.8K)
│   │   │   │   └── tick_integrity.py (4.6K) →
│   │   │   ├── base.py (3.5K) →
│   │   │   ├── checker.py (9.4K)
│   │   │   ├── diagnostic_report_generator.py (20.6K)
│   │   │   ├── exploration_log_checker.py (22.7K)
│   │   │   └── (..1 more files)
│   │   ├── phases/ (23.4K)
│   │   │   ├── completion.py (2.3K) →
│   │   │   ├── generation.py (2.1K) →
│   │   │   ├── link_cooling.py (2.0K) →
│   │   │   ├── moment_draw.py (3.4K) →
│   │   │   ├── moment_flow.py (4.3K) →
│   │   │   ├── moment_interaction.py (3.1K) →
│   │   │   ├── narrative_backflow.py (3.7K) →
│   │   │   └── rejection.py (2.4K) →
│   │   ├── cluster_presentation.py (36.8K)
│   │   ├── crystallization.py (15.9K)
│   │   ├── energy.py (36.3K) →
│   │   ├── exploration.py (42.8K)
│   │   ├── flow.py (36.3K) →
│   │   ├── nature.py (14.1K)
│   │   ├── subentity.py (39.6K)
│   │   ├── synthesis.py (23.4K) →
│   │   ├── synthesis_unfold.py (16.1K)
│   │   ├── traversal_logger.py (52.3K)
│   │   └── (..15 more files)
│   ├── schema/ (44.0K)
│   │   ├── base.py (12.6K)
│   │   ├── links.py (12.9K)
│   │   ├── nodes.py (18.5K)
│   │   └── (..2 more files)
│   ├── traversal/ (27.2K)
│   │   ├── embedding.py (7.2K) →
│   │   ├── moment.py (20.0K)
│   │   └── (..2 more files)
│   ├── cli.py (35.0K) →
│   ├── cluster_metrics.py (31.4K)
│   ├── explore_cmd.py (23.0K)
│   ├── init_cmd.py (24.5K) →
│   ├── inject.py (31.2K)
│   ├── procedure_runner.py (42.0K)
│   ├── repo_overview.py (28.5K) →
│   ├── status_cmd.py (36.3K) →
│   ├── symbol_extractor.py (49.2K) →
│   ├── validate.py (29.4K) →
│   └── (..21 more files)
├── tests/
│   ├── graph/
│   │   └── (..3 more files)
│   ├── membrane/
│   │   └── (..2 more files)
│   ├── traversal/
│   │   └── (..2 more files)
│   └── (..1 more files)
├── .mindignore (838)
├── =0.2.0 (4.2K)
├── AGENTS.md (29.9K)
├── README.md (2.9K)
└── map.md (286.9K)
```

**Docs:** `docs/cli/commands/IMPLEMENTATION_Agents_Command.md`

**Definitions:**
- `class C`
- `class AgentInfo`
- `def _get_capability_runtime()`
- `def _get_agents_from_graph()`
- `def _get_agents_from_runtime()`
- `def _format_duration()`
- `def _status_color()`
- `def list_agents()`
- `def pause_agent()`
- `def stop_agent()`
- `def kill_agent()`
- `def enable_agent()`
- `def agents_command()`

**Docs:** `docs/cli/commands/IMPLEMENTATION_Events_Command.md`

**Definitions:**
- `class C`
- `class EventInfo`
- `def _parse_time_window()`
- `def _event_type_color()`
- `def _severity_indicator()`
- `def _get_events_from_logs()`
- `def _get_events_from_graph()`
- `def _format_timestamp()`
- `def list_events()`
- `def list_errors()`
- `def events_command()`
- `def errors_command()`

**Definitions:**
- `def run()`

**Definitions:**
- `def run()`
- `def _update_sync_file()`

**Docs:** `docs/cli/commands/IMPLEMENTATION_Tasks_Command.md`

**Definitions:**
- `class C`
- `class TaskInfo`
- `def _status_color()`
- `def _priority_indicator()`
- `def _get_tasks_from_graph()`
- `def _get_tasks_from_throttler()`
- `def _format_age()`
- `def list_tasks()`
- `def tasks_command()`

**Definitions:**
- `def run()`

**Definitions:**
- `def check_mind_status()`
- `def _check_embedding_config()`
- `def _check_graph_health()`

**Definitions:**
- `def copy_capabilities()`

**Definitions:**
- `def _is_protected()`
- `def _is_excluded()`
- `def _is_actor_system_file()`
- `def _copy_actor_system()`
- `def copy_ecosystem_templates()`
- `def ignore_excluded()`

**Definitions:**
- `def create_ai_config_files()`
- `def _create_claude_md()`
- `def _create_agents_md()`
- `def _create_gemini_styleguide()`

**Definitions:**
- `def _get_embedding_config()`
- `def create_database_config()`

**Definitions:**
- `def fix_embeddings()`
- `def _load_config()`
- `def _get_current_dimension()`
- `def _fix_falkordb()`
- `def _find_nodes_needing_embeddings()`
- `def _update_node_embedding()`
- `def _update_stored_config()`
- `def _recreate_vector_indexes()`

**Definitions:**
- `def generate_embeddings()`

**Definitions:**
- `def inject_seed_yaml()`
- `def _inject_git_info()`
- `def _git_config()`
- `def _parse_github_url()`
- `def _fetch_repo_api_info()`
- `def _find_seed_files()`
- `def _inject_seed_file()`
- `def _upsert_node()`
- `def _upsert_link()`

**Definitions:**
- `def _get_embedding_dimension()`
- `def setup_database()`
- `def _ensure_docker_available()`
- `def _ensure_falkordb_running()`
- `def _create_graph_and_indexes()`

**Definitions:**
- `def validate_embedding_config()`
- `def check_embedding_config()`

**Definitions:**
- `def main()`

**Definitions:**
- `class LocalAdapter`
- `nodes()`
- `links()`

**Definitions:**
- `class RemoteAdapter`

**Definitions:**
- `getSchema()`
- `validNodeTypes()`

**Definitions:**
- `findSchemaPath()`
- `loadSchema()`
- `loadSchemaSync()`
- `clearSchemaCache()`
- `getNodeTypes()`
- `getNodeTypeMeta()`
- `getNodeFields()`
- `getLinkFields()`
- `getFieldDefault()`
- `getEnumValues()`
- `validateField()`
- `validateNode()`
- `validateLink()`
- `applyNodeDefaults()`
- `applyLinkDefaults()`

**Definitions:**
- `inferTriggerKind()`
- `inferCallType()`
- `generateEventId()`
- `extractNodeIds()`
- `generateLabel()`
- `clampDuration()`
- `normalizeFlowEvent()`
- `eventType()`
- `getDurationBucket()`
- `formatDurationForLog()`
- `getDurationColor()`

**Definitions:**
- `defaultDurationForSpeed()`
- `createRuntimeEngine()`
- `declared()`
- `makeStepperEventId()`
- `buildExplanationSentence()`

**Definitions:**
- `generateSessionId()`
- `speedToMs()`
- `extractFocusFromEvent()`
- `extractExplanationFromEvent()`

**Definitions:**
- `getEnergyBucket()`
- `formatEnergy()`

**Sections:**
- # @mind-protocol/connectome
- ## Overview
- ## Installation
- ## Usage
- ## Architecture
- ## Development

**Doc refs:**
- `agents/narrator/CLAUDE.md`
- `docs/agents/narrator/HANDOFF_Rolling_Window_Architecture.md`
- `docs/agents/narrator/HEALTH_Narrator.md`
- `docs/agents/narrator/IMPLEMENTATION_Narrator.md`
- `docs/agents/narrator/PATTERNS_Narrator.md`
- `docs/agents/narrator/SYNC_Narrator.md`
- `docs/agents/narrator/SYNC_Narrator_archive_2025-12.md`
- `docs/agents/narrator/archive/SYNC_archive_2024-12.md`

**Sections:**
- # Narrator Archive - 2024-12
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## Archived Sections (2025-12-19)
- ## HANDOFF_Rolling_Window_Architecture (Full Detail)
- # Handoff - Rolling Window Architecture
- ## The Problem
- ## The Solution: Rolling Window
- ## Why SSE (Not WebSocket)
- ## API Design
- ## Frontend Responsibilities
- ## Backend Responsibilities
- ## Generation Queue
- # 1. Return cached response immediately
- # 2. Queue generation for new clickables
- # 1. Call narrator
- # 2. Cache it
- # 3. Push to frontend
- ## Edge Cases
- ## Narrator Prompt Implications
- ## Open Questions
- ## Files Changed
- ## Next Steps
- ## TOOL_REFERENCE: Complete Example + JSON Schema (Archived)
- ## INPUT_REFERENCE: Complete Example Input (Archived)

**Doc refs:**
- `agents/narrator/CLAUDE.md`

**Sections:**
- # Narrator — Algorithm: Scene Generation
- ## CHAIN
- ## PURPOSE
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: generate_scene_output
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS
- ## ROLLING WINDOW (SUMMARY)
- ## THREAD CONTINUITY (SUMMARY)
- ## QUALITY CHECKS (MINIMUM)

**Doc refs:**
- `docs/agents/narrator/INPUT_REFERENCE.md`
- `docs/agents/narrator/TOOL_REFERENCE.md`

**Sections:**
- # Narrator — Behaviors: What the Narrator Produces
- ## CHAIN
- ## Two Response Modes
- ## Dialogue Chunks
- ## Graph Mutations
- ## SceneTree (Significant Actions)
- ## time_elapsed Rules
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS
- ## World Injection Handling
- ## Quality Indicators

**Sections:**
- # Narrator — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## HOW TO USE THIS TEMPLATE
- ## CHECKER INDEX
- ## INDICATOR: author_coherence
- ## INDICATOR: mutation_validity
- ## INDICATOR: stream_latency
- ## HOW TO RUN
- # Run narrator integration checks
- ## MARKERS

**Code refs:**
- `narrator/prompt_builder.py`
- `runtime/infrastructure/orchestration/agent_cli.py`
- `runtime/infrastructure/orchestration/narrator.py`
- `tools/stream_dialogue.py`

**Doc refs:**
- `agents/narrator/CLAUDE.md`

**Sections:**
- # Narrator — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## RUNTIME BEHAVIOR
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/orchestration/narrator.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_queries.py`

**Doc refs:**
- `agents/narrator/CLAUDE.md`
- `docs/agents/narrator/HANDOFF_Rolling_Window_Architecture.md`

**Sections:**
- # Narrator — Patterns: Why This Design
- ## Core Insight
- ## The Problem
- ## The Pattern
- ## Scope
- ## Data
- ## Behaviors Supported
- ## Behaviors Prevented
- ## Principles
- ## Dependencies
- ## Inspirations
- ## Pre-Generation Model
- ## What the Narrator Controls
- ## Free Input (Exception)
- ## Workflow (High Level)
- ## Gaps / Ideas / Questions
- ## CHAIN

**Code refs:**
- `tools/stream_dialogue.py`

**Doc refs:**
- `agents/narrator/CLAUDE.md`
- `docs/agents/narrator/BEHAVIORS_Narrator.md`
- `docs/agents/narrator/HEALTH_Narrator.md`
- `docs/agents/narrator/IMPLEMENTATION_Narrator.md`
- `docs/agents/narrator/PATTERNS_Narrator.md`
- `docs/agents/narrator/SYNC_Narrator.md`
- `docs/agents/narrator/VALIDATION_Narrator.md`
- `docs/schema/SCHEMA.md`

**Sections:**
- # Narrator — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## CHAIN

**Code refs:**
- `runtime/infrastructure/orchestration/agent_cli.py`
- `runtime/infrastructure/orchestration/narrator.py`

**Doc refs:**
- `agents/narrator/CLAUDE_old.md`
- `docs/agents/narrator/ALGORITHM_Scene_Generation.md`
- `docs/agents/narrator/BEHAVIORS_Narrator.md`
- `docs/agents/narrator/HANDOFF_Rolling_Window_Architecture.md`
- `docs/agents/narrator/HEALTH_Narrator.md`
- `docs/agents/narrator/IMPLEMENTATION_Narrator.md`
- `docs/agents/narrator/INPUT_REFERENCE.md`
- `docs/agents/narrator/PATTERNS_Narrator.md`
- `docs/agents/narrator/PATTERNS_World_Building.md`
- `docs/agents/narrator/SYNC_Narrator.md`
- `docs/agents/narrator/SYNC_Narrator_archive_2025-12.md`
- `docs/agents/narrator/TEST_Narrator.md`
- `docs/agents/narrator/TOOL_REFERENCE.md`
- `docs/agents/narrator/VALIDATION_Narrator.md`
- `docs/agents/narrator/archive/SYNC_archive_2024-12.md`

**Sections:**
- # Archived: SYNC_Narrator.md
- ## CURRENT STATE
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## RECENT CHANGES

**Sections:**
- # Player Notes — {playthrough_id}
- ## Player Setup
- ## Current Understanding
- ## Session Observations
- ## Emerging Patterns
- ## Narrator Adjustments
- ## Open Questions

**Doc refs:**
- `docs/schema/SCHEMA.md`

**Sections:**
- # Narrator Tool Reference
- ## How To Use
- # First call (starts session)
- # Subsequent calls (continues session)
- ## Output Schema (NarratorOutput)
- ## SceneTree (Significant Actions)
- ## Dialogue Chunks (Conversational Actions)
- ## Graph Mutations
- ## Time Elapsed
- ## Validation Rules (Minimum)

**Sections:**
- # Narrator — Validation: Behavioral Invariants and Output Verification
- ## CHAIN
- ## BEHAVIORS GUARANTEED
- ## OBJECTIVES COVERED
- ## INVARIANTS
- ## VERIFICATION PROCEDURE
- ## TEST COVERAGE (Snapshot)
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # World Runner — Archive (2024-12)
- ## Purpose
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## Archived From TOOL_REFERENCE.md
- ## Complete Example
- ## Validation Rules
- ## Processing Order
- ## JSON Schema (for programmatic validation)
- ## Archived From BEHAVIORS_World_Runner.md
- ## Injection as Markdown (Narrator Input)
- # WORLD INJECTION
- ## Status: INTERRUPTED
- ## EVENT: Ambush on the Road
- ## CLUSTER: Relevant Nodes
- ## WORLD CHANGES (Background)
- ## NEWS AVAILABLE
- ## Injection: Completed
- # WORLD INJECTION
- ## Status: COMPLETED
- ## WORLD CHANGES (While You Traveled)
- ## NEWS AVAILABLE
- ## ARRIVAL: York
- ## Archived From INPUT_REFERENCE.md
- ## Complete Example Input
- ## Processing Guidance
- ## CHAIN

**Sections:**
- # World Runner — Algorithm: How It Works
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## Core Principle: Runner Owns the Tick Loop
- ## ALGORITHM: run_world
- ## ALGORITHM: affects_player
- ## Algorithm Steps (Condensed)
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## Stateless Between Calls
- ## Cluster Context for Flips
- ## MARKERS
- ## CHAIN

**Sections:**
- # World Runner — Behaviors: What It Produces
- ## Injection Interface
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## OUTPUTS
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## Interrupted Injection
- ## Completed Injection
- ## Injection Queue (In-Scene Events)
- ## Event / WorldChange / News
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS
- ## Resume Pattern (Narrator)
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS
- ## CHAIN

**Sections:**
- # World Runner — Health: Verification Checklist and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## CHECKS
- ## HOW TO USE THIS TEMPLATE
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- ## INDICATOR: background_consistency
- ## INDICATOR: adapter_resilience
- ## HOW TO RUN
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/orchestration/world_runner.py`

**Doc refs:**
- `agents/world_runner/CLAUDE.md`

**Sections:**
- # World Runner — Implementation: Service Architecture and Boundaries
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## CONCURRENCY MODEL
- ## LOGIC CHAINS
- ## RUNTIME BEHAVIOR
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # World Runner Input Reference
- ## Script Location
- ## Prompt Structure
- ## Flip Context
- ## Graph Context
- ## Player Context
- ## Processing Guidance (Short)
- ## CHAIN

**Code refs:**
- `runtime/infrastructure/orchestration/world_runner.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_queries.py`

**Doc refs:**
- `agents/world_runner/CLAUDE.md`

**Sections:**
- # World Runner — Patterns: Why This Shape
- ## The Core Insight
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## Interrupt/Resume Pattern
- ## Stateless Runner
- ## What the Runner Is Not
- ## Player Impact Threshold
- ## Why Separation Matters
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS
- ## CHAIN

**Sections:**
- # World Runner — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## HANDOFF: FOR AGENTS
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## POINTERS
- ## CHAIN
- ## CONSCIOUSNESS TRACE

**Code refs:**
- `runtime/infrastructure/orchestration/world_runner.py`

**Sections:**
- # World Runner — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: adapter_resilience
- ## KNOWN GAPS

**Sections:**
- # World Runner Tool Reference
- ## WorldRunnerOutput
- ## Graph Mutations
- ## World Injection
- ## Validation Rules (Summary)
- ## Processing Order
- ## Archive Note
- ## CHAIN

**Code refs:**
- `runtime/infrastructure/orchestration/world_runner.py`

**Sections:**
- # World Runner — Validation: Service Invariants and Failure Behavior
- ## CHAIN
- ## INVARIANTS
- ## BEHAVIORS GUARANTEED
- ## OBJECTIVES COVERED
- ## HEALTH COVERAGE
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## TEST COVERAGE
- ## VERIFICATION PROCEDURE
- # No automated tests for World Runner service yet.
- ## SYNC STATUS
- ## MARKERS

**Code refs:**
- `runtime/agents/postures.py`

**Sections:**
- # Agent System — Design Patterns
- ## Purpose
- ## Architecture Overview
- ## Key Components
- # .mind/capabilities/create-doc-chain/runtime/checks.py
- # Detect missing docs
- # Build command
- # Execute
- # Success
- # Retry with feedback (up to 3 times)
- ## Data Flow
- ## Graph Schema
- ## Entry Points
- # Run work on all detected issues
- # Filter by issue type
- # List tasks
- # Spawn agent for specific issue
- # Spawn agent for task node
- ## File Structure
- ## Adding New Detection
- # Detection logic
- # runtime/agents/postures.py
- # runtime/agents/instructions.py
- ## Deprecation: Doctor Module

**Sections:**
- # ARCHITECTURE — Cybernetic Studio — Algorithm: Stimulus-to-Surface Flow
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: Stimulus-to-Surface Flow
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # ARCHITECTURE — Cybernetic Studio — Behaviors: System Observable Effects
- ## CHAIN
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # ARCHITECTURE — Cybernetic Studio — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: evidence_ref_only_storage
- ## INDICATOR: graph_ownership_boundary
- ## HOW TO RUN
- # Pending: add health runner once graph hooks exist.
- ## KNOWN GAPS
- ## MARKERS

**Sections:**
- # ARCHITECTURE — Cybernetic Studio — Implementation: Code Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## BOUNDARIES
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Cybernetic Studio Architecture
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `runtime/doctor_checks.py`

**Sections:**
- # ARCHITECTURE — Cybernetic Studio (Game + Dev Framework + Graph Layer)
- ## CHAIN
- ## 0) One-Sentence Summary
- ## 1) Validated Axioms (Non-Negotiable)
- ## 2) Repo Topology (How Many Repos, What Owns What)
- ## 3) Linking Between Repos (Three Kinds of Links)
- ## 4) Unified Ontology (Minimal Node/Link Set)
- ## 5) Evidence References (How the Graph Touches the Repo Without Duplicating It)
- ## 6) Stimulus → Energy Injection (Granular, Bottom-Up, No Overmind)
- ## 7) Physics Loop (What Runs Every Tick)
- ## 8) Places (Rooms, Views, and SYNC as Living Surfaces)
- ## 9) Agents and Identity (Story Characters vs Dev Agents)
- ## 10) Homeostasis and Safety (Prevent Runaway Refactors)
- ## 11) Concrete Deliverables (What Gets Built Where)
- ## 12) Acceptance Criteria (V1)
- ## 13) Open Questions (Explicitly Remaining)
- ## Appendix A — Minimal YAML Examples (V1)

**Doc refs:**
- `data/ARCHITECTURE — Cybernetic Studio.md`
- `docs/architecture/cybernetic_studio_architecture/ALGORITHM_Cybernetic_Studio_Process_Flow.md`
- `docs/architecture/cybernetic_studio_architecture/BEHAVIORS_Cybernetic_Studio_System_Behaviors.md`
- `docs/architecture/cybernetic_studio_architecture/HEALTH_Cybernetic_Studio_Health_Checks.md`
- `docs/architecture/cybernetic_studio_architecture/IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md`
- `docs/architecture/cybernetic_studio_architecture/PATTERNS_Cybernetic_Studio_Architecture.md`
- `docs/architecture/cybernetic_studio_architecture/SYNC_Cybernetic_Studio_Architecture_State.md`
- `docs/architecture/cybernetic_studio_architecture/VALIDATION_Cybernetic_Studio_Architectural_Invariants.md`

**Sections:**
- # Cybernetic Studio Architecture — Sync: Current State
- ## CHAIN
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## GAPS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # Pending: integration checks once graph service wiring exists.
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # ARCHITECTURE — Cybernetic Studio — Validation: Architectural Invariants
- ## CHAIN
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # Pending: add integration checks once graph service wiring exists.
- ## SYNC STATUS
- ## MARKERS

**Doc refs:**
- `docs/cli/archive/SYNC_CLI_State_Archive_2025-12.md`

**Sections:**
- # Archived: SYNC_CLI_Development_State.md
- ## STATUS
- ## CHAIN

**Code refs:**
- `runtime/doctor_checks.py`
- `runtime/repair_core.py`

**Doc refs:**
- `docs/cli/core/SYNC_CLI_Development_State.md`

**Sections:**
- # Archived: SYNC_CLI_State.md
- ## MATURITY
- ## RECENT CHANGES (ARCHIVED)
- ## NOTES
- ## RELATED ARCHIVES
- ## MERGED SNAPSHOTS
- ## CHAIN
- ## CURRENT STATE
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Code refs:**
- `cli/__main__.py`
- `cli/helpers/show_upgrade_notice_if_available.py`

**Sections:**
- # Mind CLI Core — Algorithm: Command Parsing and Execution Logic
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: `main()` in cli/__main__.py
- # Register subcommands
- ## COMMAND HANDLER ALGORITHMS
- ## DATA FLOW
- ## FUTURE COMMAND DISPATCH (PROPOSED)
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS

**Sections:**
- # Mind CLI Core — Behaviors: Observable Effects of CLI Commands
- ## CHAIN
- ## BEHAVIORS — IMPLEMENTED COMMANDS (CANONICAL)
- ## BEHAVIORS — FUTURE COMMANDS (PROPOSED)
- ## GENERIC BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS

**Sections:**
- # mind_cli_core — Health: Verification Mechanics and Coverage
- ## CHAIN
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: h_cli_command_success
- ## INDICATOR: h_cli_init_success
- ## INDICATOR: h_cli_status_accuracy
- ## INDICATOR: h_cli_embedding_fix
- ## HOW TO RUN
- # Smoke test - verify help works
- # Manual integration test
- # Run any pytest tests if available
- ## FUTURE HEALTH CHECKS (PROPOSED)

**Code refs:**
- `__main__.py`
- `check_github_for_latest_version.py`
- `check_mind_status_in_directory.py`
- `cli/__main__.py`
- `cli/commands/fix_embeddings.py`
- `cli/commands/init.py`
- `cli/commands/status.py`
- `cli/commands/upgrade.py`
- `cli/config.py`
- `copy_ecosystem_templates_to_target.py`
- `copy_runtime_package_to_target.py`
- `create_ai_config_files_for_claude_agents_gemini.py`
- `create_database_config_yaml.py`
- `create_env_example_file.py`
- `create_mcp_config_json.py`
- `fix_embeddings_for_nodes_and_links.py`
- `generate_repo_overview_maps.py`
- `get_mcp_version_from_config.py`
- `get_paths_for_templates_and_runtime.py`
- `ingest_repo_files_to_graph.py`
- `inject_seed_yaml_to_graph.py`
- `setup_database_and_apply_schema.py`
- `show_upgrade_notice_if_available.py`
- `sync_skills_to_ai_tool_directories.py`
- `update_gitignore_with_runtime_entry.py`
- `validate_embedding_config_matches_stored.py`

**Sections:**
- # mind_cli_core — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## ENTRY POINTS
- ## DATA FLOW
- ## MODULE DEPENDENCIES
- ## BIDIRECTIONAL LINKS
- ## FUTURE COMMAND MODULES (PROPOSED)

**Code refs:**
- `cli/__main__.py`

**Sections:**
- # mind_cli_core — OBJECTIVES: Core CLI Functionality and Design Goals
- ## CHAIN
- ## OBJECTIVE
- ## PRIMARY OBJECTIVES
- ## COMMAND INVENTORY
- ## CONSTRAINTS
- ## MEASUREMENT

**Code refs:**
- `__main__.py`
- `check_mind_status_in_directory.py`
- `cli/__main__.py`
- `fix_embeddings_for_nodes_and_links.py`
- `get_paths_for_templates_and_runtime.py`
- `validate_embedding_config_matches_stored.py`

**Sections:**
- # mind_cli_core — PATTERNS: Design and Implementation Conventions
- ## CHAIN
- ## PATTERNS
- # cli/commands/{command}.py
- # Implementation
- ## ANTI-PATTERNS TO AVOID

**Code refs:**
- `cli/__main__.py`
- `cli/commands/init.py`
- `cli/helpers/generate_embeddings_for_graph_nodes.py`
- `cli/helpers/ingest_repo_files_to_graph.py`
- `cli/helpers/inject_seed_yaml_to_graph.py`

**Sections:**
- # mind_cli_core — SYNC: Project State and Recent Changes
- ## CHAIN
- ## CURRENT STATUS
- ## RECENT CHANGES
- ## CODE STRUCTURE
- ## HANDOFFS
- ## KNOWN ISSUES
- ## DEPENDENCIES
- ## METRICS

**Sections:**
- # mind_cli_core — Validation: Invariants and Verification
- ## CHAIN
- ## INVARIANTS
- ## VALIDATION ID INDEX
- ## FUTURE INVARIANTS (PROPOSED)

**Code refs:**
- `mind/prompt.py`
- `runtime/cli.py`
- `runtime/prompt.py`

**Doc refs:**
- `state/SYNC_Project_State.md`

**Sections:**
- # CLI Prompt — Algorithm: Assemble the bootstrap prompt
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: `generate_bootstrap_prompt()`
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Code refs:**
- `mind/prompt.py`

**Doc refs:**
- `data/MIND Documentation Chain Pattern (Draft “Marco”).md`

**Sections:**
- # CLI Prompt — Behaviors: What the bootstrap command surfaces to agents
- ## CHAIN
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `mind/prompt.py`

**Sections:**
- # CLI Prompt — Health: Runtime verification of bootstrap guidance
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## HOW TO USE THIS TEMPLATE
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- ## HEALTH SIGNAL MAPPING
- ## VERIFICATION RESULTS
- ## INDICATOR: Prompt Doc Reference Health
- ## INDICATOR: Prompt Checklist Presence
- ## HOW TO RUN
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `mind/prompt.py`
- `runtime/cli.py`
- `runtime/prompt.py`

**Doc refs:**
- `docs/cli/prompt/ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md`

**Sections:**
- # CLI Prompt — Implementation: Code architecture and docking
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Code refs:**
- `agent_cli.py`
- `mind/prompt.py`
- `runtime/prompt.py`

**Doc refs:**
- `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`

**Sections:**
- # CLI Prompt — Patterns: Workflow that surfacing protocol context
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `runtime/prompt.py`

**Doc refs:**
- `docs/cli/core/SYNC_CLI_Development_State.md`
- `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`

**Sections:**
- # CLI Prompt Module — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Code refs:**
- `mind/prompt.py`

**Doc refs:**
- `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`
- `docs/cli/prompt/SYNC_Prompt_Command_State.md`

**Sections:**
- # CLI Prompt — Validation: Bootstrap prompt invariants
- ## CHAIN
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # ALGORITHM: Symbol Extraction
- ## Overview
- ## Phase 1: File Discovery
- ## Phase 2: Symbol Parsing (Python)
- ## Phase 3: Relationship Extraction
- ## Phase 4: Test Inference
- # TESTS: function_name, other_func
- ## Phase 5: Docs Linking
- # DOCS: docs/mind/PATTERNS_Engine.md
- ## Graph Upsert
- ## Complexity Calculation
- ## ID Patterns

**Sections:**
- # IMPLEMENTATION: Symbol Extraction
- ## File Structure
- ## Core Classes
- # ... additional type-specific fields
- # Strategies: naming, file_convention, explicit
- # Strategies: markers, references, module_convention
- ## CLI Integration
- # Standalone extraction
- # With doctor scan
- ## Data Flow
- ## Graph Schema
- ## Configuration
- # In SymbolExtractor.__init__
- # ...
- ## Entry Points

**Sections:**
- # PATTERNS: Symbol Extraction
- ## Purpose
- ## Scope
- ## Design Decisions
- ## Integration Points
- ## Related Files

**Sections:**
- # SYNC: Symbol Extraction
- ## Status: CANONICAL
- ## What's Done
- ## What's Pending
- ## Verified Working
- # Dry run extraction
- # With graph upsert
- ## Markers
- ## Last Updated

**Code refs:**
- `cli.py`
- `doctor.py`
- `mind/cli.py`
- `runtime/cli.py`
- `runtime/doctor.py`
- `runtime/repair.py`

**Sections:**
- # mind Framework CLI — Algorithm: Command Execution Logic
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: `dispatch_command()`
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # mind Framework CLI — Behaviors: Command Surface Effects
- ## CHAIN
- ## BEHAVIORS

**Sections:**
- # mind Framework CLI — Health: Verification Checklist
- ## CHAIN
- ## CHECKS

**Code refs:**
- `mind/cli.py`
- `mind/prompt.py`
- `mind/repair.py`
- `runtime/cli.py`
- `runtime/context.py`
- `runtime/core_utils.py`
- `runtime/doctor.py`
- `runtime/doctor_checks_core.py`
- `runtime/doctor_checks_metadata.py`
- `runtime/doctor_files.py`
- `runtime/init_cmd.py`
- `runtime/prompt.py`
- `runtime/repair.py`
- `runtime/repair_core.py`

**Doc refs:**
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/structure/IMPLEMENTATION_Code_Structure.md`
- `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`

**Sections:**
- # mind Framework CLI — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Cli
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # mind Framework CLI — Patterns: Command Surface Overview and Scope
- ## CHAIN
- ## PURPOSE
- ## SCOPE

**Sections:**
- # mind Framework CLI — Validation: Command Invariants
- ## CHAIN
- ## INVARIANTS

**Doc refs:**
- `docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md`
- `docs/cli/core/BEHAVIORS_CLI_Command_Effects.md`
- `docs/cli/core/HEALTH_CLI_Command_Test_Coverage.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md`
- `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`
- `docs/cli/core/SYNC_CLI_Development_State.md`
- `docs/cli/core/VALIDATION_CLI_Instruction_Invariants.md`
- `docs/cli/prompt/PATTERNS_Prompt_Command_Workflow_Design.md`
- `docs/cli/prompt/SYNC_Prompt_Command_State.md`

**Sections:**
- # CLI Modules

**Sections:**
- # ALGORITHM: Dense Clustering
- ## Overview
- ## Main Extraction Flow
- ## Phase 1: Create File Node
- # For every doc
- ## Phase 2: Parse Document Structure
- ## Phase 3: Extract Definitions
- # Input YAML in doc:
- # Output node:
- # Input YAML in doc:
- # Output node:
- # Input YAML in doc:
- # Output node:
- ## Phase 4: Extract Markers
- ## Phase 5: Resolve References
- # Check if exists
- # Create stub
- ## Phase 6: Create Links
- # Health verifies Validation
- # Dock attached to Health
- # Checker implemented by File
- # Pattern: "(V2)" or "V2" reference
- ## Phase 7: Create Moment
- # Actor expresses moment
- # Moment about all created nodes
- ## Phase 8: Upsert to Graph
- # MERGE by ID, update properties
- # MERGE relationship
- ## Complete Example
- ## Health Indicators
- ## Docks
- ## Related

**Code refs:**
- `check_health.py`

**Sections:**
- # BEHAVIORS: Dense Clustering
- ## Observable Effects
- ## Error Behaviors
- ## Related

**Code refs:**
- `tests/test_cluster_stability.py`

**Sections:**
- # HEALTH: Dense Clustering
- ## Health Indicators
- # Count before
- # Extract twice
- # Count after
- # Should be same (second run is pure update)
- ## Docks
- ## Checkers
- ## Flow
- ## Markers
- ## Related

**Code refs:**
- `runtime/cluster_metrics.py`
- `runtime/protocol_runner.py`
- `runtime/protocol_validator.py`

**Sections:**
- # IMPLEMENTATION: Cluster Metrics
- ## Overview
- ## File Locations
- ## Core Classes
- # Returns:
- # - valid: bool
- # - score: ConnectionScore
- # - target_validation: TargetValidation
- # - suggestions: List[LinkSuggestion]
- # - report: str (formatted report)
- ## Valid Target Rules
- ## Protocol Integration
- # validate_cluster enables/disables auto-validation
- # ... execute protocol ...
- # Builds cluster_summary for moment
- # Prints validation report
- # Adds errors if invalid
- # Create moment WITH cluster metrics in description
- # ... standard fields ...
- ## Usage Examples
- # ...
- ## Output Format
- ## Design Decisions
- ## Related

**Sections:**
- # IMPLEMENTATION: Dense Clustering
- ## File Structure
- ## Core Components
- # 1. File node
- # 2. Definition nodes (health, validation, checker, etc.)
- # 3. Marker nodes (TODO, escalation, proposition)
- # 4. Resolve references
- # 5. Containment links
- # 6. Create moment
- ## YAML Block Processors
- # Links to validations
- ## CLI Integration
- # In runtime/doctor.py
- # Extract structure from all docs
- # Continue with health checks...
- # In mind/cli.py
- ## Graph Queries
- ## Entry Points
- ## Related

**Sections:**
- # OBJECTIVES: Dense Clustering
- ## Primary Objective
- ## Ranked Goals
- ## Why This Order
- ## Non-Goals
- ## Success Criteria
- ## Tradeoffs Accepted
- ## Related

**Sections:**
- # PATTERNS: Dense Clustering
- ## Core Insight
- ## Design Philosophy
- ## Node Type Patterns
- ## Link Type Patterns
- ## Extraction Principles
- ## Scope
- ## Related

**Code refs:**
- `runtime/cli.py`
- `runtime/cluster_builder.py`
- `runtime/cluster_health.py`
- `runtime/doc_extractor.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/symbol_extractor.py`
- `tests/mind/test_cluster_builder.py`

**Sections:**
- # SYNC: Dense Clustering
- ## Status: DESIGNING
- ## What's Canonical
- ## What's Documented
- ## What's Implemented
- ## Implementation Plan
- ## Markers
- ## Dependencies
- ## Open Questions
- ## Last Updated

**Sections:**
- # VALIDATION: Dense Clustering
- ## Invariants
- # Before extraction
- # Extract same doc twice
- # After extraction
- # Second extraction should not increase count
- ## Threshold Violations
- ## Related

**Sections:**
- # ALGORITHM: Coverage Validation System
- ## Main Algorithm
- # 1. Load specification
- # 2. Build indices for lookup
- # 3. Validate detection → skill mapping
- # 4. Validate skill → protocol mapping
- # 5. Validate protocol files exist
- # 6. Validate protocol completeness
- # 7. Check for circular calls
- # 8. Calculate coverage
- ## Protocol Completeness Check
- # Load and parse protocol file
- # Check required step types
- # Check output section
- ## Circular Dependency Detection
- # Build adjacency list
- # Also check branch actions
- # DFS for cycle detection
- ## Report Generation
- ## Summary
- ## Status
- # Group by layer
- # Add matrix rows...
- ## Data Structures
- ## CHAIN

**Sections:**
- # BEHAVIORS: Coverage Validation System
- ## B1: Load Coverage Spec
- ## B2: Validate Detection → Skill Mapping
- ## B3: Validate Skill → Protocol Mapping
- ## B4: Validate Protocol Existence
- ## B5: Validate Protocol Completeness
- ## B6: Detect Circular Calls
- ## B7: Generate Coverage Report
- ## B8: Exit with Status
- ## B9: Show Gap Details
- ## Behavior Matrix
- ## CHAIN

**Sections:**
- # IMPLEMENTATION: Coverage Validation System
- ## Directory Structure
- # Generated
- ## Coverage Spec Format
- # specs/coverage.yaml
- # Documentation health
- # Module definition
- # Code structure
- # Health verification
- # Escalation management
- # Phase 1: Core
- # Phase 2: Doc chain
- # Phase 3: Verification
- # Phase 4: Issue handling
- # Phase 5: Full coverage
- ## Docking Points
- ## CLI Interface
- # Run validation
- # Run with verbose output
- # Generate report only (no exit code)
- # Check specific phase
- ## CI Integration
- # .github/workflows/coverage.yaml
- ## Dependencies
- ## CHAIN

**Sections:**
- # OBJECTIVES: Coverage Validation System
- ## Primary Objective
- ## Secondary Objectives
- ## Non-Objectives
- ## Success Criteria
- ## CHAIN

**Sections:**
- # PATTERNS: Coverage Validation System
- ## Core Pattern: Layered Dependency Graph
- ## Pattern: YAML as Single Source
- # specs/coverage.yaml - THE source of truth
- ## Pattern: Validator as Gate
- ## Pattern: Detection Categories
- ## Pattern: Protocol Completeness Check
- ## Pattern: Incremental Coverage
- ## Anti-Patterns
- # BAD
- # BAD
- # BAD
- # BAD - infinite loop
- ## CHAIN

**Code refs:**
- `tools/coverage/validate.py`

**Sections:**
- # SYNC: Coverage Validation System
- ## Current State
- ## The System
- ## Coverage Summary
- ## Maintenance
- ## Handoff
- ## CHAIN

**Sections:**
- # VALIDATION: Coverage Validation System
- ## V-COV-001: No Orphan Detections
- ## V-COV-002: No Orphan Skills
- ## V-COV-003: No Empty Protocol Lists
- ## V-COV-004: Protocol References Valid
- ## V-COV-005: Protocol Files Exist
- ## V-COV-006: Protocol Has Ask Step
- ## V-COV-007: Protocol Has Create Step
- ## V-COV-008: Protocol Has Output Definition
- ## V-COV-009: No Circular Protocol Calls
- ## V-COV-010: Call Targets Exist
- ## V-COV-011: Detection IDs Unique
- ## V-COV-012: Skill IDs Unique
- ## Validation Matrix
- ## CHAIN

**Doc refs:**
- `docs/infrastructure/tempo/ALGORITHM_Tempo_Controller.md`
- `docs/infrastructure/tempo/IMPLEMENTATION_Tempo.md`
- `docs/infrastructure/tempo/PATTERNS_Tempo.md`

**Sections:**
- # CONCEPT: Tempo Controller — The Main Loop That Paces Reality
- ## WHAT IT IS
- ## WHY IT EXISTS
- ## KEY PROPERTIES
- ## RELATIONSHIPS TO OTHER CONCEPTS
- ## THE CORE INSIGHT
- ## COMMON MISUNDERSTANDINGS
- ## SEE ALSO

**Code refs:**
- `mind/core_utils.py`

**Sections:**
- # Core Utils — Algorithm: Template Path Resolution and Doc Discovery
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: `get_templates_path()`
- ## ALGORITHM: `find_module_directories(docs_dir)`
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Code refs:**
- `mind/core_utils.py`

**Sections:**
- # Core Utils — Behaviors: Template Path Resolution and Docs Discovery
- ## CHAIN
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # Core Utils — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: templates_path_valid
- ## INDICATOR: docs_module_discovery_valid
- ## HOW TO RUN
- # Manual checks only
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `mind/core_utils.py`
- `runtime/core_utils.py`

**Doc refs:**
- `docs/core_utils/PATTERNS_Core_Utils_Functions.md`

**Sections:**
- # Core Utils — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Core Utils
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `mind/core_utils.py`
- `runtime/core_utils.py`

**Sections:**
- # PATTERNS: Core Utility Functions
- ## CHAIN
- ## WHY THIS SHAPE
- ## SCOPE
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## IMPLEMENTATION REFERENCES
- ## MARKERS

**Code refs:**
- `core_utils.py`
- `mind/core_utils.py`
- `runtime/core_utils.py`
- `utils.py`

**Doc refs:**
- `docs/core_utils/ALGORITHM_Core_Utils_Template_Path_And_Module_Discovery.md`
- `docs/core_utils/ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md`
- `docs/core_utils/PATTERNS_Core_Utils_Functions.md`

**Sections:**
- # SYNC: Core Utility Functions State
- ## CHAIN
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## GAPS

**Code refs:**
- `mind/core_utils.py`
- `runtime/core_utils.py`

**Sections:**
- # Core Utils — Validation: Core Utility Invariants
- ## CHAIN
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # No tests currently exist for core_utils.
- # Add tests under tests/core_utils/ if behaviors become critical.
- ## SYNC STATUS
- ## MARKERS

**Code refs:**
- `runtime/membrane/functions.py`
- `runtime/membrane/provider.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`

**Sections:**
- # Engine — Algorithm: Membrane Modulation Frame
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: compute_modulation_frame
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS
- ## COMPUTE SKELETON (V0)

**Code refs:**
- `runtime/physics/tick.py`

**Sections:**
- # Engine — Behaviors: Membrane Modulation Effects
- ## CHAIN
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `runtime/membrane/health_check.py`

**Sections:**
- # Membrane Modulation — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`

**Sections:**
- # Engine — Implementation: Membrane Modulation (Scoping + Hooks)
- ## CHAIN
- ## OVERVIEW
- ## CODE STRUCTURE (PLANNED)
- ## ENTRY POINTS (PLANNED)
- ## RESPONSIBILITIES
- ## DATA FLOW (PLANNED)
- ## MARKERS

**Code refs:**
- `runtime/physics/tick.py`

**Doc refs:**
- `docs/physics/PATTERNS_Physics.md`
- `docs/runtime/moments/PATTERNS_Moments.md`

**Sections:**
- # Engine — Patterns: Membrane Modulation (Pre-Runtime Field Shaping)
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `runtime/membrane/functions.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/physics/tick.py`

**Doc refs:**
- `docs/physics/PATTERNS_Physics.md`

**Sections:**
- # Engine — Patterns: Membrane Scoping (Per-Place Modulation)
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Doc refs:**
- `docs/physics/attention/PATTERNS_Attention_Energy_Split.md`
- `docs/runtime/membrane/BEHAVIORS_Membrane_Modulation.md`
- `docs/runtime/membrane/PATTERNS_Membrane_Modulation.md`
- `docs/runtime/membrane/PATTERNS_Membrane_Scoping.md`
- `docs/runtime/membrane/SYNC_Membrane_Modulation.md`

**Sections:**
- # Membrane Modulation — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## IN PROGRESS
- ## TODO
- ## POINTERS

**Code refs:**
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/physics/tick.py`

**Sections:**
- # Engine — Validation: Membrane Modulation Invariants
- ## CHAIN
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # No automated tests yet
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/embeddings/service.py`

**Sections:**
- # Data Models — Algorithm: Pydantic Data Flow and Validation
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: model_instantiate_and_validate
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # Data Models — Behaviors: Consistent Data Interactions
- ## CHAIN
- ## OVERVIEW
- ## BEHAVIORS
- ## MARKERS

**Sections:**
- # Data Models — Health: Pydantic Schema Integrity
- ## PURPOSE OF THIS FILE
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: model_validation_success
- ## HOW TO RUN
- # Execute all tests for the data models module
- # Run Pydantic schema consistency checks
- ## MARKERS

**Code refs:**
- `runtime/models/__init__.py`
- `runtime/models/base.py`
- `runtime/models/links.py`
- `runtime/models/nodes.py`

**Doc refs:**
- `docs/mind/models/PATTERNS_Models.md`
- `docs/mind/models/VALIDATION_Models.md`
- `docs/schema/models/PATTERNS_Pydantic_Schema_Models.md`

**Sections:**
- # Data Models — Implementation: Pydantic Code Architecture
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # Data Models — Objectives
- ## CHAIN
- ## PURPOSE
- ## OBJECTIVES
- ## OBJECTIVE CONFLICTS
- ## NON-OBJECTIVES
- ## VERIFICATION

**Sections:**
- # Data Models — Patterns: Pydantic for Graph Schema Enforcement
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `nodes.py`
- `runtime/models/base.py`
- `runtime/models/links.py`
- `runtime/models/nodes.py`

**Doc refs:**
- `docs/mind/models/HEALTH_Models.md`
- `docs/mind/models/PATTERNS_Models.md`

**Sections:**
- # Data Models — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## Agent Observations
- ## GAPS
- ## CHAIN

**Sections:**
- # Data Models — Validation: Pydantic Invariants and Properties
- ## CHAIN
- ## OVERVIEW
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # Run all tests for data models
- # Run tests specifically for base models and enums
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # Moment Graph Engine — Validation: Player DMZ Invariants (Stub)
- ## CHAIN
- # Note: PATTERNS and BEHAVIORS files planned but not yet created
- ## BEHAVIORS GUARANTEED
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/canon/canon_holder.py`

**Sections:**
- # Moment Graph Engine — Validation: Simultaneity + CONTRADICTS (Stub)
- ## CHAIN
- # Note: PATTERNS and BEHAVIORS files planned but not yet created
- ## BEHAVIORS GUARANTEED
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## VERIFICATION PROCEDURE
- ## MARKERS

**Code refs:**
- `runtime/physics/tick.py`

**Sections:**
- # Moment Graph Engine — Validation: Void Pressure (Stub)
- ## CHAIN
- # Note: PATTERNS and BEHAVIORS files planned but not yet created
- ## BEHAVIORS GUARANTEED
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## MARKERS

**Code refs:**
- `runtime/moment_graph/traversal.py`

**Sections:**
- # Moment Graph Engine — Algorithm: Click, Wait, Surfacing
- ## CHAIN
- ## CLICK TRAVERSAL
- ## WAIT TRIGGER TRAVERSAL
- ## SURFACING AND DECAY
- ## SCENE CHANGE
- ## DRAMATIC BOOST

**Code refs:**
- `runtime/moment_graph/__init__.py`

**Sections:**
- # Moment Graph Engine — Behaviors: Traversal And Surfacing
- ## CHAIN
- ## OBSERVABLE BEHAVIORS
- ## INPUTS AND OUTPUTS
- ## SIDE EFFECTS

**Code refs:**
- `runtime/moment_graph/__init__.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_queries.py`

**Sections:**
- # Moment Graph Engine — Implementation: Runtime Layout
- ## CHAIN
- ## FILES AND ROLES
- ## DATA FLOW
- ## DEPENDENCIES

**Sections:**
- # Moment Graph Engine — Objectives
- ## CHAIN
- ## PURPOSE
- ## OBJECTIVES
- ## OBJECTIVE CONFLICTS
- ## NON-OBJECTIVES
- ## VERIFICATION

**Code refs:**
- `runtime/moment_graph/__init__.py`

**Sections:**
- # Moment Graph Engine — Patterns: Instant Traversal Hot Path
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DEPENDENCIES
- ## WHAT THIS DOES NOT SOLVE
- ## MARKERS

**Code refs:**
- `runtime/moment_graph/__init__.py`
- `runtime/moment_graph/queries.py`

**Sections:**
- # Moment Graph Engine — Sync: Current State
- ## CHAIN
- ## MATURITY
- ## CURRENT STATE
- ## HANDOFF: FOR AGENTS
- ## TODO
- ## CONFLICTS
- ## Agent Observations
- ## ARCHIVE

**Code refs:**
- `runtime/moment_graph/__init__.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`

**Doc refs:**
- `docs/physics/attention/VALIDATION_Attention_Split_And_Interrupts.md`

**Sections:**
- # Archived: SYNC_Moment_Graph_Engine.md
- ## RECENT CHANGES

**Code refs:**
- `runtime/moment_graph/traversal.py`
- `runtime/tests/test_e2e_moment_graph.py`
- `runtime/tests/test_moment_graph.py`

**Sections:**
- # Moment Graph Engine — Tests: Runtime Coverage
- ## CHAIN
- ## EXISTING TESTS
- ## HOW TO RUN
- # Requires FalkorDB running on localhost:6379
- ## GAPS

**Code refs:**
- `runtime/moment_graph/traversal.py`

**Sections:**
- # Moment Graph Engine — Validation: Traversal Invariants
- ## CHAIN
- ## INVARIANTS
- ## PERFORMANCE EXPECTATIONS
- ## FAILURE MODES TO WATCH

**Code refs:**
- `runtime/moments/__init__.py`

**Doc refs:**
- `docs/schema/SCHEMA_Moments.md`

**Sections:**
- # Moment Graph — Algorithm: Graph Operations
- ## CHAIN
- ## OVERVIEW
- ## TARGET FLOW
- ## DATA SOURCES

**Code refs:**
- `runtime/moments/__init__.py`

**Doc refs:**
- `docs/schema/SCHEMA_Moments.md`

**Sections:**
- # Moment Graph — Behaviors: Moment Lifecycle
- ## CHAIN
- ## BEHAVIOR SUMMARY
- ## EXPECTED BEHAVIORS
- ## NOTES

**Code refs:**
- `runtime/moments/__init__.py`

**Sections:**
- # Moment Graph — Implementation: Stub Layout
- ## CHAIN
- ## FILES
- ## CURRENT IMPLEMENTATION NOTES

**Sections:**
- # Moment Graph — Objectives
- ## CHAIN
- ## PURPOSE
- ## OBJECTIVES
- ## OBJECTIVE CONFLICTS
- ## NON-OBJECTIVES
- ## VERIFICATION

**Code refs:**
- `runtime/moments/__init__.py`

**Sections:**
- # Moment Graph — Patterns
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DEPENDENCIES
- ## WHAT THIS DOES NOT SOLVE
- ## MARKERS

**Code refs:**
- `runtime/moments/__init__.py`

**Doc refs:**
- `docs/runtime/moments/PATTERNS_Moments.md`
- `docs/runtime/moments/SYNC_Moments.md`
- `docs/schema/SCHEMA_Moments.md`

**Sections:**
- # Moment Graph — Sync: Current State
- ## CHAIN
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## HANDOFF: FOR AGENTS
- ## TODO

**Code refs:**
- `runtime/moments/__init__.py`
- `runtime/tests/test_e2e_moment_graph.py`
- `runtime/tests/test_moment_graph.py`
- `runtime/tests/test_moment_lifecycle.py`
- `runtime/tests/test_moments_api.py`

**Sections:**
- # Moment Graph — Test Coverage
- ## CHAIN
- ## CURRENT COVERAGE
- ## GAPS
- ## HOW TO RUN

**Code refs:**
- `runtime/moments/__init__.py`

**Doc refs:**
- `docs/schema/SCHEMA_Moments.md`

**Sections:**
- # Moment Graph — Validation: Invariants
- ## CHAIN
- ## INVARIANTS
- ## VERIFICATION NOTES

**Sections:**
- # Self-Improvement — Algorithm
- ## CHAIN
- ## OVERVIEW
- ## PHASE 1: TRIGGER
- # 1. Check if improvement loop is already running
- # 2. Validate trigger
- # 3. Compute urgency
- # 4. Start improvement cycle
- # Severity based on how far past threshold
- # Based on pattern impact
- ## PHASE 2: OBSERVE
- # 1. Read from source
- # 2. Filter relevant signals
- # 3. Normalize to common schema
- # 4. Add to signal set
- # 5. Compute aggregates
- # Exploration aggregates
- # Anomaly aggregates
- # Agent aggregates
- # Graph aggregates
- ## PHASE 3: DIAGNOSE
- # 1. Recurring anomalies
- # 2. Metric drift
- # 3. Correlation patterns
- # 1. Start at symptom layer (Output)
- # 2. Gather evidence for each layer
- # 3. Find root cause layer (first layer that explains pattern)
- # 4. Check pattern library for known patterns
- ## PHASE 4: PROPOSE
- # 1. Check known fixes first
- # 2. Generate layer-specific proposals
- # 3. Score and rank proposals
- # 4. Add validation plans
- # Constant tuning proposals
- # Formula change proposals (higher risk)
- # Factors
- # Scoring formula
- # Bonus for known fixes
- ## PHASE 5: VALIDATE
- # Run new logic alongside old, compare outputs
- # Deploy to subset, monitor
- # Randomized comparison
- # Queue for human validation
- ## PHASE 6: APPROVE
- # Auto-approve conditions
- # Notify (auto but with notification)
- # Require human approval
- # Default: queue for approval
- # Human-readable summary
- # Actions
- ## PHASE 7: DEPLOY
- # 1. Create backup
- # 2. Apply change
- # 3. Run verification tests
- # 4. Start monitoring
- # 5. Record deployment
- # 1. Restore backup
- # 2. Verify restoration
- # 3. Notify humans
- # 4. Mark proposal as failed
- # 5. Record for learning
- ## PHASE 8: LEARN
- # 1. Record pattern → diagnosis mapping
- # 2. Record successful fixes
- # 3. Record failed fixes (to avoid repeating)
- # 4. Update pattern recognition
- ## KEY FORMULAS
- ## CONFIGURATION
- ## COMPLEXITY

**Sections:**
- # Self-Improvement — Behaviors
- ## CHAIN
- ## PURPOSE
- ## BEHAVIORS
- ## ANTI-BEHAVIORS
- ## EDGE CASES
- ## INPUTS
- ## OUTPUTS
- ## OBJECTIVES COVERAGE
- ## BEHAVIOR DEPENDENCIES

**Sections:**
- # Self-Improvement — Health
- ## CHAIN
- ## PURPOSE
- ## WHEN TO USE HEALTH VS TESTS
- ## HEALTH INDICATORS
- # Get weekly improvement counts
- # Compute trend
- ## META-HEALTH
- ## HEALTH CHECK FLOW
- ## HEALTH CHECKER INDEX
- ## MANUAL REVIEW CHECKLIST
- ## Self-Improvement Health Review: {date}
- ## EXAMPLE HEALTH REPORT
- ## DOCKING POINTS
- ## HOW TO RUN
- # Run all health checks
- # Run specific check
- # Run meta-health only
- # Generate report

**Code refs:**
- `approval/notifications.py`
- `approval/queue.py`
- `approval/tiers.py`
- `config.py`
- `deployment/backup.py`
- `deployment/deployer.py`
- `deployment/monitor.py`
- `deployment/rollback.py`
- `diagnosis/evidence.py`
- `diagnosis/layer_attribution.py`
- `diagnosis/pattern_detector.py`
- `learning/embeddings.py`
- `learning/extractor.py`
- `learning/pattern_library.py`
- `loop.py`
- `models.py`
- `proposals/generator.py`
- `proposals/scorer.py`
- `proposals/types.py`
- `signals/aggregator.py`
- `signals/collector.py`
- `validation/modes/shadow.py`
- `validation/modes/unit_test.py`
- `validation/validator.py`

**Sections:**
- # Self-Improvement — Implementation
- ## CHAIN
- ## CODE STRUCTURE
- ## FILE RESPONSIBILITIES
- ## DESIGN PATTERNS
- ## ENTRY POINTS
- ## DATA FLOW
- ## STATE MANAGEMENT
- ## CONFIGURATION
- # mind/data/config/improvement_config.yaml
- # Trigger thresholds
- # Observation
- # Validation
- # Deployment
- # Approval
- # Learning
- # Meta
- ## DEPENDENCIES
- ## BIDIRECTIONAL LINKS
- # mind/improvement/loop.py:1
- ## TESTS
- ## IMPLEMENTATION ORDER

**Sections:**
- # Self-Improvement — Objectives
- ## CHAIN
- ## VISION
- ## OBJECTIVES (Ranked)
- ## OBJECTIVE RELATIONSHIPS
- ## PRIORITY TIERS
- ## NON-OBJECTIVES
- ## SUCCESS CRITERIA
- ## TENSION POINTS

**Sections:**
- # Self-Improvement — Patterns
- ## CHAIN
- ## DESIGN PHILOSOPHY
- ## CORE PRINCIPLES
- ## SCOPE
- ## ARCHITECTURE PRINCIPLES
- ## RELATIONSHIPS TO OTHER MODULES
- ## DESIGN DECISIONS

**Sections:**
- # Self-Improvement — Sync
- ## CHAIN
- ## CURRENT STATE
- ## KNOWN GAPS
- ## RISKS
- ## HANDOFFS
- ## DOCUMENTATION STATUS
- ## NEXT ACTIONS
- ## CHANGELOG
- ## ARCHIVE

**Sections:**
- # Archived: SYNC_SelfImprovement.md
- ## MATURITY
- ## DEPENDENCIES
- ## IMPLEMENTATION PLAN
- ## VERIFICATION COMMANDS
- # (When implemented)
- # Run improvement loop health check
- # Run invariant verification
- # Run unit tests
- # Check pattern library

**Sections:**
- # Self-Improvement — Validation
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- # Backup exists
- # Backup is valid
- # Rollback mechanism tested for this type
- # Must be low risk constant tune
- # Must have human approval
- # Minimum occurrences
- # Evidence exists
- # Evidence is traceable
- # Root layer identified
- # Evidence for root layer
- # Evidence is non-empty
- # Type-specific checks
- # Observation overhead
- # Concurrent cycles
- # Check oldest cycle duration
- # If there was a deployment, fix should be recorded
- # Should have triggered rollback
- # Check meta-cycle frequency
- # Check recent meta-changes had REQUIRE tier
- ## PRIORITY TABLE
- ## INVARIANT INDEX
- ## VERIFICATION PROCEDURE
- # Block on CRITICAL failures
- ## TESTING REQUIREMENTS

**Sections:**
- # Engine — Algorithm: High-Level Flow
- ## CHAIN
- ## HIGH-LEVEL FLOW

**Sections:**
- # Engine — Behaviors: Runtime Effects
- ## CHAIN
- ## BEHAVIORS

**Sections:**
- # Engine — Health: Verification
- ## CHAIN
- ## HEALTH CHECKS

**Sections:**
- # Engine — Implementation: Code Mapping
- ## CHAIN
- ## CODE LOCATIONS
- ## NOTES

**Sections:**
- # OBJECTIVES — Engine
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Engine — Patterns: Runtime Ownership And Boundaries
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES

**Sections:**
- # Engine — Sync: Current State
- ## CHAIN
- ## CURRENT STATE
- ## TODO

**Sections:**
- # Engine — Validation: Invariants
- ## CHAIN
- ## INVARIANTS

**Code refs:**
- `frontend/app/scenarios/page.tsx`
- `frontend/app/start/page.tsx`
- `frontend/hooks/useGameState.ts`
- `runtime/infrastructure/api/playthroughs.py`
- `runtime/init_db.py`
- `runtime/physics/graph/graph_ops.py`

**Sections:**
- # API — Algorithm
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: create_scenario_playthrough
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS
- ## Graph Helpers
- ## Health Check
- ## Debug Mutation Stream
- ## Playthrough Creation
- ## CHAIN

**Code refs:**
- `app.py`
- `graph_ops_moments.py`
- `narrator.py`
- `orchestrator.py`
- `surface.py`

**Sections:**
- # Player Input → Moment Output Flow
- ## Overview
- ## Fast Path: Word Click
- ## Full Path: Action
- ## Thresholds
- ## Validation
- # 1. Create playthrough
- # 2. Get current moments
- # 3. Click a word (get moment_id from step 2)
- # 4. Verify weight changed
- # Action with narrator
- ## Chain

**Code refs:**
- `runtime/infrastructure/api/graphs.py`
- `runtime/infrastructure/api/playthroughs.py`

**Sections:**
- # Graph Management API
- ## Purpose
- ## Endpoints
- ## Implementation Notes
- ## Migration: What Moves to blood-ledger
- ## Status

**Sections:**
- # API — Behaviors
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## Health Check
- ## Debug Mutation Stream
- ## ANTI-BEHAVIORS
- ## MARKERS
- ## CHAIN

**Code refs:**
- `runtime/infrastructure/api/app.py`
- `runtime/tests/test_moments_api.py`
- `runtime/tests/test_router_schema_validation.py`

**Sections:**
- # API — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- ## INDICATOR: api_availability
- ## MANUAL RUN
- # Verify API Health
- # Verify Action Loop
- ## KNOWN GAPS

**Sections:**
- # API — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # API — Patterns
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS
- ## CHAIN

**Code refs:**
- `app.py`
- `runtime/infrastructure/api/app.py`
- `runtime/infrastructure/api/moments.py`
- `runtime/tests/test_moments_api.py`
- `runtime/tests/test_router_schema_validation.py`

**Doc refs:**
- `docs/infrastructure/api/IMPLEMENTATION_Api.md`
- `docs/infrastructure/api/PATTERNS_Api.md`

**Sections:**
- # API — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## HANDOFF: FOR AGENTS
- ## TODO
- ## POINTERS
- ## CHAIN

**Code refs:**
- `runtime/infrastructure/api/app.py`
- `runtime/infrastructure/api/playthroughs.py`

**Doc refs:**
- `docs/infrastructure/api/ALGORITHM_Api.md`
- `docs/infrastructure/api/ALGORITHM_Playthrough_Creation.md`
- `docs/infrastructure/api/BEHAVIORS_Api.md`
- `docs/infrastructure/api/IMPLEMENTATION_Api.md`
- `docs/infrastructure/api/PATTERNS_Api.md`
- `docs/infrastructure/api/SYNC_Api.md`
- `docs/infrastructure/api/TEST_Api.md`
- `docs/infrastructure/api/VALIDATION_Api.md`

**Sections:**
- # Archived: SYNC_Api.md
- ## RECENT CHANGES

**Code refs:**
- `runtime/tests/test_moments_api.py`
- `runtime/tests/test_router_schema_validation.py`

**Doc refs:**
- `docs/infrastructure/api/SYNC_Api.md`

**Sections:**
- # API — Validation
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## TEST COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## CHAIN

**Sections:**
- # DatabaseAdapter — Algorithm
- ## CHAIN
- ## PURPOSE
- ## A1: Factory Initialization
- ## A2: FalkorDB Query Execution
- ## A3: Neo4j Query Execution
- ## A4: Transaction Handling
- # FalkorDB doesn't have explicit transactions in the same way
- # Queries are atomic individually
- # For multi-query atomicity, use MULTI/EXEC at Redis level
- # On exception, commands not executed = implicit rollback
- ## A5: Index Creation
- ## A6: Health Check
- ## A7: Connection Recovery
- # Neo4j driver handles connection pooling internally
- # Just verify connectivity
- ## VERIFICATION

**Sections:**
- # DatabaseAdapter — Behaviors
- ## CHAIN
- ## PURPOSE
- ## BEHAVIOR TABLE
- ## DETAILED BEHAVIORS
- ## CYPHER COMPATIBILITY BEHAVIORS
- ## VERIFICATION

**Sections:**
- # DatabaseAdapter — Health
- ## CHAIN
- ## PURPOSE
- ## HEALTH SIGNALS
- ## HEALTH CHECK IMPLEMENTATION
- # runtime/infrastructure/database/health.py
- # H1: Connection status
- # H1: Latency threshold
- ## MONITORING INTEGRATION
- ## RUNBOOK
- ## VERIFICATION

**Code refs:**
- `runtime/connectome/persistence.py`
- `runtime/connectome/session.py`
- `runtime/doctor_graph.py`
- `runtime/graph/health/check_health.py`
- `runtime/infrastructure/api/graphs.py`
- `runtime/infrastructure/database/__init__.py`
- `runtime/infrastructure/database/adapter.py`
- `runtime/infrastructure/database/factory.py`
- `runtime/infrastructure/database/falkordb_adapter.py`
- `runtime/infrastructure/database/neo4j_adapter.py`
- `runtime/init_db.py`
- `runtime/migrations/migrate_to_v2_schema.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_ops_apply.py`
- `runtime/physics/graph/graph_ops_moments.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_queries.py`
- `runtime/physics/graph/graph_queries_moments.py`
- `runtime/physics/graph/graph_queries_search.py`
- `runtime/physics/graph/graph_query_utils.py`
- `runtime/physics/health/checkers/energy_conservation.py`
- `runtime/physics/health/checkers/moment_lifecycle.py`
- `runtime/tests/test_energy_v1_2.py`
- `runtime/tests/test_moments_api.py`
- `tools/archive/migrate_schema_v11.py`
- `tools/migrate_v11_fields.py`
- `tools/test_health_live.py`

**Sections:**
- # DatabaseAdapter — Implementation
- ## CHAIN
- ## PURPOSE
- ## NEW FILES TO CREATE
- ## EXISTING FILES TO MODIFY
- ## FULL FILE LIST (31 files with FalkorDB references)
- ## ADAPTER INTERFACE
- # runtime/infrastructure/database/adapter.py
- ## FACTORY FUNCTION
- # runtime/infrastructure/database/factory.py
- ## MIGRATION PATTERN
- # Current: Direct FalkorDB usage
- # Target: Adapter usage
- ## IMPLEMENTATION ORDER
- ## VERIFICATION

**Sections:**
- # DatabaseAdapter — Objectives
- ## CHAIN
- ## PURPOSE
- ## OBJECTIVES
- ## OBJECTIVE CONFLICTS
- ## NON-OBJECTIVES
- ## VERIFICATION

**Sections:**
- # DatabaseAdapter — Patterns
- ## CHAIN
- ## PURPOSE
- ## CORE PATTERN: Strategy + Factory
- # Factory creates the right adapter based on config
- # All consumers use the same interface
- ## DESIGN DECISIONS
- # .mind/database_config.yaml
- # Neo4j can run as-is
- # May need to rewrite some patterns
- # Backend-specific implementation
- ## SCOPE
- ## COMPATIBILITY NOTES
- ## VERIFICATION

**Code refs:**
- `app/api/connectome/tick/route.ts`
- `graph_interface.py`
- `runtime/graph/health/lint_terminology.py`
- `runtime/graph/health/test_schema.py`
- `runtime/infrastructure/api/graphs.py`
- `runtime/init_db.py`
- `runtime/migrations/migrate_001_schema_alignment.py`
- `runtime/migrations/migrate_temporal_v171.py`
- `runtime/migrations/migrate_tick_to_tick_created.py`
- `runtime/migrations/migrate_to_content_field.py`
- `runtime/migrations/migrate_to_v2_schema.py`
- `runtime/physics/graph/adapters/__init__.py`
- `runtime/physics/graph/adapters/base.py`
- `runtime/physics/graph/adapters/falkordb_adapter.py`
- `runtime/physics/graph/adapters/mock_adapter.py`
- `runtime/physics/graph/adapters/neo4j_adapter.py`
- `runtime/physics/graph/graph_interface.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_queries.py`

**Sections:**
- # Database Adapter — Patterns: Graph Backend Abstraction
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- # Current (wrong)
- # Target (right)
- # mind/data/physics_config.yaml
- ## DEPENDENCIES
- ## SCOPE
- ## REQUIRED CHANGES INVENTORY
- ## CYPHER DIALECT DIFFERENCES
- ## MARKERS

**Code refs:**
- `__init__.py`
- `adapter.py`
- `factory.py`
- `falkordb_adapter.py`
- `neo4j_adapter.py`
- `runtime/connectome/persistence.py`
- `runtime/connectome/session.py`
- `runtime/infrastructure/api/graphs.py`
- `runtime/init_db.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_queries.py`

**Sections:**
- # DatabaseAdapter — Sync
- ## CHAIN
- ## CURRENT STATE
- ## IMPLEMENTATION CHECKLIST
- ## RECENT CHANGES
- ## HANDOFF
- ## DEPENDENCIES
- ## VERIFICATION

**Code refs:**
- `__init__.py`
- `app/api/connectome/tick/route.ts`
- `base.py`
- `falkordb_adapter.py`
- `graph_ops.py`
- `graph_ops_read_only_interface.py`
- `graph_queries.py`
- `mock_adapter.py`
- `neo4j_adapter.py`
- `runtime/connectome/persistence.py`
- `runtime/connectome/runner.py`
- `runtime/connectome/steps.py`
- `runtime/graph/health/lint_terminology.py`
- `runtime/graph/health/test_schema.py`
- `runtime/infrastructure/api/graphs.py`
- `runtime/infrastructure/memory/moment_processor.py`
- `runtime/infrastructure/orchestration/world_runner.py`
- `runtime/infrastructure/tempo/tempo_controller.py`
- `runtime/init_db.py`
- `runtime/migrations/migrate_001_schema_alignment.py`
- `runtime/migrations/migrate_temporal_v171.py`
- `runtime/migrations/migrate_tick_to_tick_created.py`
- `runtime/migrations/migrate_to_content_field.py`
- `runtime/migrations/migrate_to_v2_schema.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`
- `runtime/physics/exploration.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_ops_apply.py`
- `runtime/physics/graph/graph_ops_links.py`
- `runtime/physics/graph/graph_ops_moments.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_queries.py`
- `runtime/physics/graph/graph_queries_moments.py`
- `runtime/physics/graph/graph_queries_search.py`
- `runtime/physics/tick_v1_2.py`

**Sections:**
- # SYNC — Database Adapter
- ## Current State
- ## Maturity
- ## Files Requiring Changes
- ## Implementation Order
- ## Decisions Made
- ## Open Questions
- ## Handoff Notes

**Sections:**
- # DatabaseAdapter — Validation
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- # Same query on both
- # Failing transaction
- # Node should not exist
- # With backend: falkordb
- # Reset singleton, change config to neo4j
- # Even with bad connection
- # Should not execute DROP, just search for literal string
- ## TEST MATRIX
- ## CRITICAL TESTS
- # test_database_adapter.py
- # Filter out infrastructure/database
- # This should return bool, not raise
- ## VERIFICATION

**Sections:**
- # Scene Memory System — Legacy Archive (2024-12)
- ## PURPOSE
- ## LEGACY SUMMARY
- ## CANONICAL REFERENCES
- ## NOTE ON REMOVALS

**Code refs:**
- `runtime/infrastructure/memory/transcript.py`
- `runtime/models/nodes.py`
- `runtime/physics/graph/graph_ops.py`

**Sections:**
- # Scene Memory System — Algorithm (Legacy)
- ## CHAIN
- ## STATUS
- ## LEGACY ALGORITHM OUTLINE
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: process_scene_memory (legacy)
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS
- ## CANONICAL REFERENCES
- ## NEXT IN CHAIN

**Sections:**
- # Scene Memory System — Behavior (Legacy)
- ## CHAIN
- ## STATUS
- ## LEGACY BEHAVIOR SUMMARY
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## ANTI-BEHAVIORS
- ## MARKERS
- ## LEGACY EDGE CASES
- ## NEXT IN CHAIN

**Sections:**
- # Scene Memory — Health: Verification Checklist
- ## CHAIN
- ## CHECKS

**Code refs:**
- `runtime/infrastructure/memory/__init__.py`
- `runtime/infrastructure/memory/moment_processor.py`

**Sections:**
- # Scene Memory System — Implementation: Moment Processing Architecture
- ## CHAIN
- ## CODE STRUCTURE
- ## ENTRY POINTS
- ## DATA FLOW (SUMMARY)
- ## LOGIC CHAINS
- ## CONCURRENCY MODEL
- ## MODULE DEPENDENCIES
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Scene-Memory
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Scene Memory System — Pattern (Legacy)
- ## CHAIN
- ## STATUS
- ## PRINCIPLES
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## LEGACY PATTERN SUMMARY
- ## LEGACY LIMITS
- ## NEXT IN CHAIN

**Code refs:**
- `runtime/infrastructure/api/moments.py`
- `runtime/infrastructure/memory/moment_processor.py`
- `runtime/physics/graph/graph_ops_moments.py`
- `runtime/physics/graph/graph_queries_moments.py`

**Sections:**
- # Scene Memory System — Sync
- ## ARCHITECTURE EVOLUTION
- ## IMPLEMENTATION STATUS
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## REPAIR LOG (2025-12-20)
- ## OPEN QUESTIONS
- ## ARCHIVE

**Code refs:**
- `moment_processor.py`
- `runtime/infrastructure/memory/__init__.py`
- `runtime/infrastructure/memory/moment_processor.py`
- `runtime/models/nodes.py`
- `runtime/tests/test_moment.py`

**Sections:**
- # Archived: SYNC_Scene_Memory.md
- ## Maturity
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## MOMENT NODE TYPE
- # Moment Graph fields
- # Tick tracking
- # Transcript reference
- ## MOMENT PROCESSOR API
- # Immediate moments (added to transcript)
- # Potential moments (graph only)
- # Links
- ## CHANGELOG
- # Archived: SYNC_Scene_Memory.md
- ## RECENT CHANGES
- # Archived: SYNC_Scene_Memory.md
- ## DOCUMENT CHAIN
- ## REPAIR LOG (2025-12-19)
- ## Agent Observations

**Code refs:**
- `mind/tests/test_moment.py`
- `runtime/tests/test_e2e_moment_graph.py`
- `runtime/tests/test_moment_graph.py`
- `runtime/tests/test_moment_lifecycle.py`
- `runtime/tests/test_moments_api.py`

**Sections:**
- # Scene Memory System — Test: Moment Processing Coverage
- ## CHAIN
- ## TEST STRATEGY
- ## UNIT TESTS
- ## INTEGRATION TESTS
- ## EDGE CASES
- ## TEST COVERAGE
- ## HOW TO RUN
- # Run MomentProcessor unit tests
- # Run full moment-related suite
- ## KNOWN TEST GAPS
- ## FLAKY TESTS
- ## MARKERS

**Sections:**
- # Scene Memory System — Validation (Legacy)
- ## CHAIN
- ## STATUS
- ## LEGACY INVARIANTS (SUMMARY)
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## LEGACY TEST NOTES
- ## TEST COVERAGE
- ## VERIFICATION PROCEDURE
- ## MARKERS
- ## NEXT IN CHAIN

**Code refs:**
- `runtime/infrastructure/tempo/tempo_controller.py`
- `runtime/physics/tick.py`

**Sections:**
- # Tempo Controller — Algorithm: Tick Loop and Pacing
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: run
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/tempo/tempo_controller.py`

**Sections:**
- # Tempo Controller — Behaviors: Observable Pacing Effects
- ## CHAIN
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/tempo/health_check.py`

**Sections:**
- # Tempo Controller — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## HOW TO USE THIS TEMPLATE
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- ## INDICATOR: tempo_tick_advances
- ## HOW TO RUN
- # Run all health checks for this module
- # Run a specific checker
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/api/tempo.py`
- `runtime/infrastructure/canon/canon_holder.py`
- `runtime/infrastructure/tempo/tempo_controller.py`
- `runtime/physics/tick.py`

**Sections:**
- # Tempo Controller — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Tempo
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `runtime/infrastructure/api/tempo.py`
- `runtime/infrastructure/tempo/tempo_controller.py`
- `runtime/physics/tick.py`

**Sections:**
- # Tempo Controller — Patterns: Pacing the Main Loop
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `runtime/infrastructure/tempo/tempo_controller.py`

**Doc refs:**
- `docs/infrastructure/canon/PATTERNS_Canon.md`
- `docs/infrastructure/tempo/ALGORITHM_Tempo_Controller.md`
- `docs/infrastructure/tempo/PATTERNS_Tempo.md`

**Sections:**
- # Tempo Controller — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Code refs:**
- `runtime/infrastructure/tempo/tempo_controller.py`

**Sections:**
- # Tempo Controller — Validation: Pacing Invariants
- ## CHAIN
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # No automated tests yet
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # WSL autostart (systemd user)
- ## 1) Activer systemd dans WSL
- ## 2) Activer linger pour l'auto-start
- ## 3) Binaries et chemins absolus
- ## 4) Configurer le frontend
- ## 5) Installer les units systemd
- ## 6) Config ngrok v3
- ## 7) Logs et status
- ## 8) Checks de sante
- ## 9) Depannage

**Code refs:**
- `runtime/llms/gemini_agent.py`

**Sections:**
- # mind LLM Agents — Algorithm: Gemini Stream Flow
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## ALGORITHM: main
- ## DATA FLOW
- ## COMPLEXITY
- ## DATA STRUCTURES
- ## KEY DECISIONS
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # mind LLM Agents — Behaviors: Gemini Agent Output
- ## CHAIN
- ## BEHAVIORS
- ## NOTES
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `gemini_agent.py`
- `mind/llms/gemini_agent.py`

**Doc refs:**
- `docs/cli/HEALTH_CLI_Coverage.md`

**Sections:**
- # mind LLM Agents — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## HOW TO USE THIS TEMPLATE
- ## CHECKER INDEX
- ## INDICATOR: Stream Validity
- ## INDICATOR: api_connectivity
- ## HOW TO RUN
- # Manual verification of stream JSON
- # Manual verification of plain text
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `agent_cli.py`
- `gemini_agent.py`
- `mind/llms/gemini_agent.py`
- `runtime/agent_cli.py`
- `runtime/llms/gemini_agent.py`
- `runtime/llms/tool_helpers.py`

**Sections:**
- # mind LLM Agents — Implementation: Code Architecture
- ## CHAIN
- ## CODE STRUCTURE
- ## MODULE LAYOUT
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Llm Agents
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `agent_cli.py`
- `mind/llms/gemini_agent.py`

**Sections:**
- # mind LLM Agents — Patterns: Provider-Specific LLM Subprocesses
- ## CHAIN
- ## THE PROBLEM
- ## SCOPE
- ## DATA
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## WHAT THIS DOES NOT SOLVE
- ## MARKERS

**Code refs:**
- `gemini_agent.py`
- `runtime/agent_cli.py`
- `runtime/llms/gemini_agent.py`

**Sections:**
- # LLM Agents — Sync: Current State
- ## CHAIN
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## TODO
- ## ARCHIVE
- ## ARCHIVE

**Code refs:**
- `runtime/agent_cli.py`
- `runtime/llms/gemini_agent.py`

**Doc refs:**
- `docs/llm_agents/ALGORITHM_Gemini_Stream_Flow.md`
- `docs/llm_agents/BEHAVIORS_Gemini_Agent_Output.md`
- `docs/llm_agents/HEALTH_LLM_Agent_Coverage.md`
- `docs/llm_agents/IMPLEMENTATION_LLM_Agent_Code_Architecture.md`
- `docs/llm_agents/PATTERNS_Provider_Specific_LLM_Subprocesses.md`
- `docs/llm_agents/SYNC_LLM_Agents_State.md`
- `docs/llm_agents/SYNC_LLM_Agents_State_archive_2025-12.md`
- `docs/llm_agents/VALIDATION_Gemini_Agent_Invariants.md`

**Sections:**
- # Archived: SYNC_LLM_Agents_State.md
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## RECENT CHANGES
- ## TODO
- # No module-specific tests documented yet.
- # Archived: SYNC_LLM_Agents_State.md
- ## RECENT CHANGES
- ## Agent Observations

**Doc refs:**
- `docs/llm_agents/PATTERNS_Provider_Specific_LLM_Subprocesses.md`

**Sections:**
- # mind LLM Agents — Validation: Gemini Agent Invariants
- ## CHAIN
- ## BEHAVIORS GUARANTEED
- ## OBJECTIVES COVERED
- ## INVARIANTS
- ## EDGE CASES
- ## VERIFICATION METHODS
- ## FAILURE MODES
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## MARKERS

**Doc refs:**
- `templates/CLAUDE_ADDITION.md`
- `templates/CODEX_SYSTEM_PROMPT_ADDITION.md`

**Sections:**
- # mind Framework — Algorithm: Overview
- ## CHAIN
- ## OVERVIEW
- ## CONTENTS
- ## ALGORITHM: Install Protocol in Project
- ## ALGORITHM: Agent Starts Task
- ## ALGORITHM: Create New Module
- ## ALGORITHM: Modify Existing Module
- ## ALGORITHM: Document Cross-Cutting Concept
- ## NOTES

**Doc refs:**
- `templates/CODEX_SYSTEM_PROMPT_ADDITION.md`

**Sections:**
- # mind Framework — Implementation: Overview
- ## CHAIN
- ## OVERVIEW
- ## FILE STRUCTURE
- ## SCHEMAS AND CONFIG
- ## FLOWS AND LINKS
- # DOCS: docs/{area}/{module}/PATTERNS_*.md

**Sections:**
- # ALGORITHM: Project Health Doctor
- ## OVERVIEW
- ## ID CONVENTION
- # Issues
- # Objectives
- # Tasks
- # Spaces (modules)
- # Things (files)
- # Semantic links (with role name)
- # Structural links
- ## MAIN FLOW
- ## 1. FETCH OBJECTIVES
- # Example: narrative_OBJECTIVE_engine-physics-documented
- # Objective-specific fields
- ## 2. SURFACE ISSUES
- # ... etc
- # Each failure becomes an issue
- # TEST_FAILED, TEST_ERROR, TEST_TIMEOUT
- # Each failure becomes an issue
- # HEALTH_FAILED, INVARIANT_VIOLATED
- # Example: narrative_ISSUE_monolith-engine-physics-graph-ops_a7
- ## {TASK_TYPE}
- # Issue-specific fields
- # Space contains Issue
- # Issue relates to Thing (file)
- # Update: severity, message, detected_at, status=open
- # Create new with links
- ## 3. TRAVERSE UP
- # Step 1: Find Space
- # ID: space_MODULE_{module}
- # Step 2: Check doc chain exists
- # Step 3: Find objective
- # ID: narrative_OBJECTIVE_{module}-{type}
- # → narrative_OBJECTIVE_engine-physics-documented
- # Determine outcome
- ## 4. CREATE TASKS
- # Example: narrative_TASK_serve-engine-physics-documented_01
- ## Task: Serve documented for engine-physics
- # Task-specific fields
- # Task serves Objective (direction: support)
- # Task includes Issue (direction: subsume)
- # Issue blocks Objective (direction: oppose)
- # Group by outcome
- # SERVE tasks: group by objective, split if > MAX
- # Create links
- # RECONSTRUCT tasks: one per module with gaps
- # TRIAGE tasks: one per orphan module
- ## 5. OUTPUT
- ## OBJECTIVE → SKILL MAPPING
- ## ISSUE TYPE → OBJECTIVE MAPPING
- ## CLI INTEGRATION
- # Basic doctor (static only)
- # With tests
- # With health checks
- # Full (static + tests + health)
- # Output formats
- # Show tasks only
- ## AUTO-RESOLVE
- ## CHAIN

**Sections:**
- # BEHAVIORS: Project Health Doctor
- ## COMMAND INTERFACE
- # Basic health check
- # With specific directory
- # Output formats
- # Filter by severity
- # Specific checks
- ## HEALTH CHECKS
- ## SPECIAL MARKERS
- ## OUTPUT BEHAVIOR
- ## Critical (2 issues)
- ## Warnings (3 issues)
- ## Info (3 issues)
- ## Suggested Actions
- ## GUIDED REMEDIATION
- ## Current State
- ## Recommended Steps
- # DOCS: docs/api/PATTERNS_Api_Design.md
- ## Template Commands
- # Generate PATTERNS from template
- ## Reference
- ## EXIT CODES
- ## CONFIGURATION
- # Thresholds
- # Ignore patterns
- # Disable specific checks
- # Custom severity overrides
- ## FALSE POSITIVE SUPPRESSION
- ## DOC TEMPLATE DRIFT DEFERMENTS
- ## NON-STANDARD DOC TYPE DEFERMENTS
- ## RESOLVED ESCALATION MARKERS
- ## MARKER STANDARDIZATION
- ## CHAIN

**Code refs:**
- `doctor_checks.py`
- `doctor_report.py`
- `runtime/doctor.py`

**Sections:**
- # Project Health Doctor — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- ## INDICATOR: Score Sanity
- ## HOW TO RUN
- # Run all doctor checks on the current project
- # Run with JSON output for machine parsing
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `runtime/doctor.py`
- `runtime/doctor_checks.py`
- `runtime/doctor_checks_content.py`
- `runtime/doctor_checks_core.py`
- `runtime/doctor_checks_docs.py`
- `runtime/doctor_checks_metadata.py`
- `runtime/doctor_checks_naming.py`
- `runtime/doctor_checks_prompt_integrity.py`
- `runtime/doctor_checks_quality.py`
- `runtime/doctor_checks_reference.py`
- `runtime/doctor_checks_stub.py`
- `runtime/doctor_checks_sync.py`
- `runtime/doctor_files.py`

**Sections:**
- # Project Health Doctor — Implementation: Code architecture and docking
- ## CHAIN
- ## CODE STRUCTURE
- ## DATA FLOW
- ## DOC-LINK COMPLIANCE
- ## LOCATIONS
- ## GAPS / IDEAS

**Sections:**
- # PATTERNS: Project Health Doctor
- ## THE PROBLEM
- ## THE INSIGHT
- ## DESIGN DECISIONS
- ## WHAT WE CHECK
- ## WHAT WE DON'T CHECK
- ## ALTERNATIVES CONSIDERED
- ## CHAIN

**Code refs:**
- `doctor.py`
- `runtime/doctor_checks.py`

**Sections:**
- # SYNC: Project Health Doctor
- ## CURRENT STATE
- ## IMPLEMENTATION ORDER
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## GAPS
- ## CHAIN
- ## ARCHIVE

**Code refs:**
- `runtime/doctor.py`
- `runtime/solve_escalations.py`

**Doc refs:**
- `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`
- `docs/cli/prompt/SYNC_Prompt_Command_State.md`

**Sections:**
- # Archived: SYNC_Project_Health_Doctor.md
- ## MATURITY
- ## TODO
- ## NEW MARKERS (2025-12-29 Review)

**Sections:**
- # VALIDATION: Project Health Doctor
- ## INVARIANTS
- ## CHECK CORRECTNESS
- ## OUTPUT FORMAT CORRECTNESS
- ## EDGE CASES
- ## PERFORMANCE BOUNDS
- ## VERIFICATION COMMANDS
- # Verify determinism
- # Verify exit codes
- # Verify JSON validity
- # Verify ignore patterns
- ## CHAIN

**Sections:**
- # Agent Trace Logging — Behaviors: Observable Effects
- ## CHAIN
- ## COMMANDS
- ## AUTOMATIC TRACING
- ## TRACE FILE FORMAT
- ## INTEGRATION POINTS
- ## Usage (auto-generated)
- ## WHAT GETS TRACED
- ## WHAT DOESN'T GET TRACED

**Sections:**
- # Agent Trace Logging — Patterns: Why This Design
- ## CHAIN
- ## THE PROBLEM
- ## THE INSIGHT
- ## DESIGN DECISIONS
- ## WHAT THIS ENABLES
- ## TRADEOFFS
- ## ALTERNATIVES CONSIDERED
- ## OPEN QUESTIONS

**Code refs:**
- `runtime/cli.py`

**Sections:**
- # Agent Trace Logging — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IMPLEMENTATION PLAN
- ## HANDOFF: FOR AGENTS
- ## TODO
- ## OPEN QUESTIONS
- ## MARKERS

**Sections:**
- # mind Framework — Algorithm: Overview
- ## CHAIN
- ## ENTRY POINT

**Sections:**
- # mind Framework — Behaviors: Observable Protocol Effects
- ## CHAIN
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `mind/validate.py`
- `runtime/prompt.py`

**Doc refs:**
- `docs/cli/HEALTH_CLI_Coverage.md`

**Sections:**
- # mind Framework — Health: Protocol Verification and Mechanics
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- ## INDICATOR: Chain Completeness
- ## HOW TO RUN
- # Verify protocol health for the current project
- # Verify a specific module
- ## KNOWN GAPS
- ## MARKERS

**Sections:**
- # mind Framework — Implementation: Overview
- ## CHAIN
- ## ENTRY POINT

**Sections:**
- # OBJECTIVES — Protocol
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # mind Framework — Patterns: Bidirectional Documentation Chain for AI Agent Workflows
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- # Descriptive names
- # Not
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## WHAT THIS DOES NOT SOLVE
- ## MARKERS

**Code refs:**
- `runtime/cli.py`

**Doc refs:**
- `archive/SYNC_archive_2024-12.md`
- `templates/CLAUDE_ADDITION.md`
- `templates/mind/PRINCIPLES.md`
- `templates/mind/PROTOCOL.md`

**Sections:**
- # mind Framework — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## STRUCTURE
- ## POINTERS
- ## ARCHIVE
- ## Agent Observations
- ## GAPS
- ## ARCHIVE

**Sections:**
- # Archived: SYNC_Protocol_Current_State.md
- ## NEW MARKERS (2025-12-29 Review)

**Code refs:**
- `scripts/check_chain_links.py`
- `scripts/check_doc_completeness.py`
- `scripts/check_doc_refs.py`
- `scripts/check_orphans.py`

**Sections:**
- # mind Framework — Validation: Protocol Invariants
- ## CHAIN
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # Check all invariants
- # Check specific invariant
- # Check specific module
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # ALGORITHM: MCP Tools
- ## graph_query Algorithm
- # Derive context automatically
- # Process queries in parallel
- # Create embedding for query
- # Search local graph by similarity
- # Expand to connected nodes if requested
- ## membrane_query Algorithm
- # Connect to membrane graph (hardcoded endpoint)
- # Search membrane graph (public nodes only)
- # Each match includes org_id
- ## vector_search Algorithm
- # Get all nodes with embeddings
- # Apply filter if specified
- # Calculate cosine similarity
- # Sort by score descending
- # Return top k
- ## procedure_start Algorithm
- # Load procedure definition
- # Create session
- # Return first step
- ## procedure_continue Algorithm
- # Validate answer
- # Store answer
- # Advance to next step
- # Check if complete
- # Return next step
- ## doctor_check Algorithm
- # Run health checks based on depth
- # Auto-fix small schema issues
- # Assign agents to remaining issues
- ## agent_spawn Algorithm
- # Determine agent
- # Check availability
- # Set running
- # Execute
- # Set ready
- ## Embedding Algorithm
- # Use configured embedding service
- # Default: all-mpnet-base-v2, 768 dimensions
- ## CHAIN

**Sections:**
- # BEHAVIORS: MCP Tools
- ## Query Tool Behaviors
- ## Procedure Tool Behaviors
- ## Agent Tool Behaviors
- ## Task Tool Behaviors
- ## Doctor Tool Behaviors
- ## What Agents Cannot Do
- ## Error Behaviors
- ## CHAIN

**Code refs:**
- `runtime/connectome/runner.py`

**Sections:**
- # MCP Tools — Health: Verification Mechanics and Coverage
- ## WHEN TO USE HEALTH (NOT TESTS)
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: h_session_valid
- ## INDICATOR: h_step_ordering
- ## INDICATOR: h_cluster_complete
- ## HOW TO RUN
- # Run all membrane health checks (when implemented)
- # Run specific checker (via tests for now)
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `mcp/server.py`
- `runtime/connectome/runner.py`
- `runtime/connectome/steps.py`
- `runtime/connectome/validation.py`
- `runtime/physics/exploration.py`
- `runtime/physics/subentity.py`

**Sections:**
- # IMPLEMENTATION: MCP Tools
- ## Code Structure
- ## Key Components
- ## Data Flow
- ## Configuration
- ## Extension Points
- ## Tests
- # Run exploration tests
- # Run MCP server tests
- # Run procedure tests
- ## CHAIN

**Sections:**
- # Doctor Issues to Protocols Mapping
- ## How It Works
- ## Issue → Protocol → Skill Mapping
- ## Protocol Dependency Graph
- ## Auto-Fix Flow
- # Load skill for context
- # Run protocol via membrane
- ## Issue Detection → Protocol Trigger Examples
- ## Adding New Issue Types

**Code refs:**
- `mind/repair_verification.py`
- `runtime/repair_verification.py`

**Sections:**
- # MAPPING: Issue Type to Verification
- ## CHAIN
- ## QUICK REFERENCE
- ## DETAILED CHECKS
- ## GLOBAL CHECKS (all issue types)
- ## MARKERS

**Sections:**
- # Skills and Protocols Mapping
- ## Doctor → Skill → Protocol Flow
- ## Skills Inventory
- ## Protocols Inventory
- ## Protocol Dependencies
- ## Doctor → Protocol Mapping Summary
- ## Implementation Priority
- ## Files to Create
- ## CHAIN

**Code refs:**
- `doctor_checks.py`
- `engine/connectome/persistence.py`
- `engine/connectome/schema.py`
- `repair_verification.py`
- `runtime/doctor_checks_membrane.py`
- `runtime/repair.py`
- `runtime/repair_core.py`
- `runtime/repair_verification.py`
- `tools/coverage/validate.py`

**Sections:**
- # Archived: SYNC_MCP_Tools.md
- ## Maturity
- ## Recent Changes
- # Archived: SYNC_MCP_Tools.md (Section 2)
- ## v1.2 Features (Complete)
- # ━━━ ATTRIBUTE EXPLANATIONS ━━━
- # id: "{space_id}"
- # WHAT: Unique identifier
- # WHY: Used in all graph queries
- # FORMAT: space_<area>_<module>
- ## Next Steps

**Code refs:**
- `mind/repair_verification.py`

**Sections:**
- # VALIDATION: Completion Verification System
- ## PURPOSE
- ## CHAIN
- ## ARCHITECTURE
- ## VERIFICATION CHECKS BY ISSUE TYPE
- ## GLOBAL VERIFICATION REQUIREMENTS
- ## AGENT RESTART PROTOCOL
- ## VERIFICATION FAILED
- ## IMPLEMENTATION NOTES
- ## MARKERS

**Sections:**
- # VALIDATION: MCP Tools
- ## Query Invariants
- ## Procedure Invariants
- ## Graph Invariants
- ## Agent Invariants
- ## Doctor Invariants
- ## SubEntity Invariants
- ## Error Conditions
- ## CHAIN

**Doc refs:**
- `docs/physics/ALGORITHM_Physics.md`
- `docs/physics/SYNC_Physics.md`
- `docs/physics/TEST_Physics.md`

**Sections:**
- # Physics — Validation: Invariants
- ## CHAIN
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## TEST COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## Core Invariants
- # No state stored outside graph
- # (This is architectural, not queryable)
- # Verify: handlers don't cache state
- # Verify: no files store moment state
- # Verify: display queue reads from graph
- # Physics tick runs continuously
- # (Verify via tick counter)
- # THEN links only from completed moments
- # THEN links must have tick
- # No THEN links deleted in test run
- # (Track count before/after)
- # All moments created by handler X are ATTACHED_TO character X
- # (This requires tracking handler outputs)
- # Verify in handler code:
- # - No writes to other character's moments
- # - No direct graph modifications outside ATTACHED_TO scope
- # Spoken moments cannot revert to possible
- # THEN links are permanent
- # (No DELETE on THEN links in codebase)
- # Run same scenario at 1x and 3x
- # Compare THEN link chains
- # Should be identical (display differs, canon same)
- # Sum of all weights before tick
- # Tick
- # Sum after = before - decay + injection
- # Handlers only triggered by flip
- # (Verify handler trigger conditions in code)
- # No cooldown logic in handler system
- # No artificial caps on handler runs per tick
- ## Graph State Invariants
- # Status must be valid enum
- # Spoken moments must have tick_resolved
- # Decayed moments must have tick_resolved
- # Weight must be 0-1
- # CAN_SPEAK weight must be 0-1
- # CAN_SPEAK must originate from Character
- # ATTACHED_TO targets must be valid types
- # THEN links connect Moments only
- ## Physics Invariants
- # At 3x speed, total decay over 10 seconds real-time
- # should equal decay at 1x over 10 seconds real-time
- # Same state → same flips
- # After player input, something responds (eventually)
- # Run physics until stable or max ticks
- # Either NPC responded or player character observed silence
- ## Handler Invariants
- # Handler must produce valid moment drafts
- # Handler does NOT set weight
- # Handler output only attaches to its character
- # When injected, should only attach to Aldric
- ## Canon Invariants
- # Two characters grabbing same item should BOTH canonize
- # Both should flip (high weight)
- # Both should be canon
- # Action processing handles the conflict, not canon holder
- # Same character, incompatible actions → mutex
- # Only one should canonize (higher weight)
- ## Speed Invariants
- # At 3x, low-weight moments still create THEN links
- # Not displayed (below threshold)
- # But is canon
- # At 3x, interrupt moments always display
- # Must display (combat is interrupt)
- # Speed should drop to 1x
- ## Action Invariants
- # Actions process one at a time
- # First succeeds
- # Second gets blocked consequence
- # Stale action fails validation
- # Sword already taken by someone else
- # Action should fail validation
- ## Question Answering Invariants
- # Handler doesn't wait for QA
- # Should complete in LLM time, not LLM time × 2 (waiting for QA)
- # QA cannot contradict existing facts
- # Aldric already has a father defined
- # QA for "who is my father" must return existing, not invent new
- # Should reference existing father, not create new one
- ## Performance Benchmarks
- # Setup: 1000 moments, 50 characters, 20 places
- # Setup: 10000 moments
- # 4 characters flip simultaneously
- # Should be ~1 LLM call time, not 4
- ## Verification Checklist
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## TEST COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS

**Doc refs:**
- `docs/physics/SYNC_Physics.md`
- `docs/physics/TEST_Physics.md`

**Sections:**
- # Physics — Validation: Procedures
- ## CHAIN
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## TEST COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # Physics — Algorithm: Energy Flow Sources Sinks And Moment Dynamics (consolidated)
- ## CHAIN
- ## CONSOLIDATION

**Code refs:**
- `runtime/moment_graph/queries.py`
- `runtime/physics/cluster_energy_monitor.py`
- `runtime/physics/display_snap_transition_checker.py`
- `runtime/physics/graph/graph_ops_moments.py`
- `runtime/physics/graph/graph_queries.py`
- `runtime/tests/test_cluster_energy_monitor.py`
- `runtime/tests/test_physics_display_snap.py`

**Doc refs:**
- `algorithms/ALGORITHM_Physics_Mechanisms.md`

**Sections:**
- # Physics — Algorithm: Energy Mechanics And Link Semantics
- ## CHAIN
- ## Energy Mechanics
- ## NODE TYPES
- ## LINK TYPES
- ## NARRATIVE TYPES
- ## LINK STRENGTH
- ## STRENGTH MECHANICS (Six Categories)
- # Speaking is stronger than thinking
- # Direct address is strongest
- # Speaker's belief activated
- # ABOUT links activated
- # Check what this evidence supports
- # Check what this evidence contradicts
- # Create new association if co-occurrence is strong enough
- # Recent narratives in same conversation
- # Co-occurring narratives associate
- # How much does receiver trust source?
- # Average trust from relationship narratives
- # Direct witness vs secondhand
- # Higher cost = stronger commitment
- # What beliefs motivated this action?
- # Narrative pressure (from contradictions and energy)
- # Danger
- # Emotional weight of moment
- # All strength changes multiplied by intensity
- ## Consolidated: Energy Flow Sources, Sinks, And Moment Dynamics
- ## ENERGY SOURCES
- # Baseline regeneration
- # State modifier
- # Pump budget
- # Distribute by belief strength only
- # Things don't hold energy — redirect to related narratives
- # Character arrives — they bring their energy with them
- # News creates/energizes a narrative
- # Discovery energizes existing narrative
- # Draw energy from involved characters
- # Inject into related narratives
- ## ENERGY SINKS
- # Core types resist decay
- # Draw from speakers
- # Draw from attached narratives
- ## ENERGY TRANSFER (Links)
- # A pulls from B
- # B pulls from A
- # Energy flows toward equilibrium
- # Additional drain: old loses extra (world moved on)
- # Things don't hold energy — skip
- # Forward flow
- # Reverse flow only if bidirectional
- # Only if character is awake and present
- # Only nodes with energy
- # Reverse flow: target → moment
- # Partial drain — recent speech still has presence
- # Status change
- # Remaining energy decays normally from here
- ## MOMENT ENERGY & WEIGHT
- ## Consolidated: Tick Cycle Gating, Flips, And Dispatch
- ## FULL TICK CYCLE
- # 1. Characters pump into narratives
- # 2. Narrative-to-narrative transfer
- # 3. ABOUT links (focal point pulls)
- # 4. Moment energy flow
- # 5. Narrative pressure injection (structural pressure)
- # 6. Decay (energy leaves system)
- # 7. Detect energy threshold crossings
- # Energy decay (fast)
- # Check for status transition
- # Weight decay (slow, only without reinforcement)
- ## PHYSICAL GATING
- ## PARAMETERS
- ## EMERGENT BEHAVIORS
- ## M11: FLIP DETECTION
- # Check still valid (state may have changed)
- # Flip to active
- # Handler needed?
- # Async - handler will call record_to_canon when done
- # Direct record
- # ... process ...
- ## M12: CANON HOLDER
- # 1. Status change
- # 2. Energy cost (actualization)
- # 3. THEN link (history chain)
- # 4. Time passage
- # 5. Strength mechanics
- # 6. Actions
- # 7. Notify frontend
- # ABOUT links activated
- # Confirming evidence
- # Contradicting evidence
- # Recent narratives in same conversation
- # Adjust by text length
- # Check for time-based events
- # Decay check (large time jumps)
- # Apply Commitment mechanic (M5)
- # Winner proceeds to canon
- # Loser returns to possible, decayed
- ## M13: AGENT DISPATCH
- # Detect and process energy threshold crossings
- # Scheduled events
- ## WHAT WE DON'T DO
- ## Consolidated: Handler And Input Processing Flows
- ## Player Input Processing
- # Character names
- # Also check nicknames, titles
- # Place names
- # Thing names
- # ATTACHED_TO player (they said it)
- # ATTACHED_TO current location
- # ATTACHED_TO all present characters (they heard it)
- # REFERENCES for recognized names/things (strong energy transfer)
- # CAN_SPEAK link (player spoke this)
- # Direct references get full energy
- # Boost all moments attached to this character
- # All present characters get partial energy (they heard)
- ## "Aldric, what do you think?"
- ## Aldric directly referenced → full energy boost
- ## "What does everyone think?"
- ## No direct reference → distributed partial energy
- # 1. Parse
- # 2. Create moment
- # 3. Create links
- # 4. Inject energy
- # 5. Emit player moment to display (immediate)
- # 6. Trigger physics tick (may be immediate based on settings)
- # After physics tick, check if anything flipped
- # No response from NPCs
- # Energy flows back to player character
- # Player character's handler will produce observation
- # "The silence stretches. No one meets your eye."
- # Or: pause until submit
- ## Question Answering
- ## In character handler
- # Handler needs to know about father
- # Queue question for answering
- # Handler continues with what it knows
- # Does NOT block waiting for answer
- # 1. GATHER — Get relevant existing facts
- # 2. GENERATE — Invent answer via LLM
- # 3. VALIDATE — Check consistency
- # 4. INJECT — Create nodes in graph
- # Character's existing family
- # Character's origin place
- # Character's existing beliefs/narratives
- # Historical events character witnessed
- # Check family conflicts
- # Check place conflicts
- # Check temporal conflicts
- # Create new character nodes
- # Create relationship link
- # Create new place nodes
- # Create relationship link
- # Create potential memory moments
- # Create ANSWERED_BY link for traceability
- ## After injection, physics handles integration:
- ## New father character exists
- ## Memory moments attached to asker exist
- ## These have initial weight (e.g., 0.4)
- ## Next tick:
- ## - Energy propagates through FAMILY links
- ## - Memory moments may get boosted if relevant
- ## - If weight crosses threshold, memory surfaces
- ## No special "integrate answer" logic
- ## Just physics
- ## Consolidated: Speed Control And Display Filtering
- ## Speed Controller
- # Player character directly addressed
- # Combat initiated
- # Major character arrival
- # Energy threshold crossed (narrative pressure)
- # Decision point (player choices available)
- # Discovery (new significant narrative)
- # Danger to player or companions
- # Phase 1: Running (player sees this already)
- # - Motion blur effect
- # - Muted colors
- # - Text small, streaming upward
- # Phase 2: The Beat (300-500ms)
- # Phase 3: Arrival
- # - Crystal clear, full color
- # - Large, centered, deliberate
- # Player can resume after input processed
- ## At 3x, low-weight moments:
- ## - Actualize in graph ✓
- ## - Create THEN links ✓
- ## - Become history ✓
- ## - Display to player ✗ (filtered)
- ## Player can review history later
- ## Mechanisms — Function-Level Map (consolidated)

**Sections:**
- # Physics — Algorithm: Handler And Input Processing Flows (consolidated)
- ## CHAIN
- ## CONSOLIDATION

**Code refs:**
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`
- `runtime/physics/contradiction_pressure_from_negative_polarity_mechanism.py`
- `runtime/physics/graph/graph_ops_moments.py`
- `runtime/physics/graph/graph_queries.py`
- `runtime/physics/primes_lag_and_half_life_decay_mechanism.py`
- `runtime/physics/tick.py`

**Doc refs:**
- `algorithms/ALGORITHM_Physics_Mechanisms.md`

**Sections:**
- # Physics — Algorithm: Mechanisms (Energy, Pressure, Surfacing)
- ## CHAIN
- ## CONSOLIDATION

**Code refs:**
- `diffusion_sim_v2.py`

**Sections:**
- # Physics — Algorithm: Schema v1.2 Energy Physics
- ## CHAIN
- ## CORE MODEL
- ## MOMENT LIFECYCLE
- ## ENERGY PHASES (Per Tick)
- # No cap — decay handles runaway energy naturally
- # Unified formula (v1.2: no conductivity)
- # Transfer
- # Link receives injection (tracks attention)
- # Hebbian: color link with moment's emotions
- # Base flow (v1.2: no conductivity)
- # Apply path resistance from speaker
- # Hebbian coloring
- # Link energy decays fast (attention fades)
- # Node energy decays based on weight
- # Liquidate to all connected nodes
- # Moment remains as graph bridge
- ## PATH RESISTANCE
- # Each edge: low weight = high resistance
- # Total = sum of edge resistances on shortest path
- ## EMOTION MECHANICS
- # Inherit from source's current focused state
- ## LINK CRYSTALLIZATION
- # Create with inherited emotions
- ## REDIRECT MECHANICS (Override)
- # Find new targets
- # Emotion proximity determines transfer rate
- # Remainder "haunts" original narrative
- ## AGENT RESPONSIBILITIES
- ## EXAMPLE: Full Scene Trace
- ## SCHEMA CHANGES (v1.1)
- # Note: conductivity removed in v1.2 — weight controls flow rate
- # Note: strength merged into weight in v1.2 — weight now dual-purpose
- # No energy_capacity — decay handles runaway energy naturally
- ## CONSTANTS
- ## VALIDATION
- ## MARKERS

**Sections:**
- # Physics — Algorithm: Speed Control And Display Filtering (consolidated)
- ## CHAIN
- ## CONSOLIDATION

**Sections:**
- # Physics — Algorithm: Tick Cycle Gating Flips And Dispatch (consolidated)
- ## CHAIN
- ## CONSOLIDATION

**Code refs:**
- `runtime/physics/tick.py`

**Doc refs:**
- `implementation/IMPLEMENTATION_Physics_Architecture.md`
- `implementation/IMPLEMENTATION_Physics_Code_Structure.md`
- `implementation/IMPLEMENTATION_Physics_Dataflow.md`
- `implementation/IMPLEMENTATION_Physics_Runtime.md`

**Sections:**
- # Physics — Implementation: Code Architecture and Structure
- ## CHAIN
- ## OVERVIEW
- ## DOCUMENT LAYOUT
- ## SIGNPOSTS

**Code refs:**
- `runtime/physics/cluster_energy_monitor.py`
- `runtime/physics/display_snap_transition_checker.py`
- `runtime/physics/tick.py`

**Doc refs:**
- `docs/physics/SYNC_Physics.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Mechanisms.md`

**Sections:**
- # Physics — Sync History (2025-12)
- ## RECENT CHANGES

**Code refs:**
- `graph_ops.py`
- `graph_ops_apply.py`
- `graph_ops_events.py`
- `graph_ops_image.py`
- `graph_ops_types.py`
- `graph_queries.py`
- `graph_queries_search.py`
- `runtime/handlers/base.py`
- `runtime/infrastructure/api/moments.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/traversal.py`
- `runtime/physics/tick.py`

**Doc refs:**
- `docs/physics/ALGORITHM_Physics.md`
- `docs/physics/BEHAVIORS_Physics.md`
- `docs/physics/IMPLEMENTATION_Physics.md`
- `docs/physics/PATTERNS_Physics.md`
- `docs/physics/SYNC_Physics.md`
- `docs/physics/SYNC_Physics_archive_2025-12.md`
- `docs/physics/TEST_Physics.md`
- `docs/physics/VALIDATION_Physics.md`

**Sections:**
- # Archived: SYNC_Physics.md
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## Agent Observations
- # Archived: SYNC_Physics.md
- ## RECENT CHANGES
- ## Agent Observations
- # Archived: SYNC_Physics.md
- ## CHAIN

**Code refs:**
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`

**Sections:**
- # Physics — Algorithm: Attention Energy Split
- ## CHAIN
- ## OVERVIEW
- ## PROCEDURE (ABRIDGED)

**Code refs:**
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`

**Sections:**
- # Physics — Behaviors: Attention Split and Interrupts
- ## CHAIN
- ## BEHAVIORS
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`

**Sections:**
- # Physics — Implementation: Attention Energy Split
- ## CHAIN
- ## CODE MAP
- ## NOTES

**Sections:**
- # Physics — Objectives: Attention Energy Split
- ## CHAIN
- ## PURPOSE
- ## OBJECTIVES
- ## OBJECTIVE CONFLICTS
- ## NON-OBJECTIVES
- ## VERIFICATION

**Code refs:**
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`
- `runtime/physics/tick.py`

**Doc refs:**
- `docs/physics/PATTERNS_Physics.md`
- `docs/runtime/membrane/PATTERNS_Membrane_Scoping.md`
- `docs/runtime/moments/PATTERNS_Moments.md`

**Sections:**
- # Physics — Patterns: Attention Energy Split (Focus Redistribution as Physics)
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## INTERRUPT PATTERN
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`

**Sections:**
- # Physics — Sync: Attention Energy Split
- ## CURRENT STATE
- ## RECENT CHANGES
- ## TODO

**Code refs:**
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`

**Sections:**
- # Physics — Validation: Attention Split + Interrupt Invariants
- ## CHAIN
- ## BEHAVIORS GUARANTEED
- ## INVARIANTS (MUST ALWAYS HOLD)
- ## PROPERTIES (PROPERTY-BASED TESTS)
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- ## SYNC STATUS
- ## GAPS / QUESTIONS

**Sections:**
- # Cluster Presentation Algorithm
- ## Overview
- ## ALGORITHM: Post-Traversal Selection
- # Default: highest alignment
- # Dead ends (no outgoing links)
- # Weak links (permanence < 0.3)
- # Filter by relevance to intention
- # Best link by weight × energy × alignment
- # Ensure main path intact
- ## ALGORITHM: Synthesis Unfolding
- # Input: "surprising reliable the Revelation, incandescent (ongoing)"
- # Prefix emotions → adverbs
- # Energy level
- # Status
- # Input: "suddenly definitively establishes, with admiration"
- # Pre-modifiers → adverbs
- # Verb → participle
- # Post-modifiers stay same
- ## ALGORITHM: Presentation Formatting
- # v1.9.1: Add content block if present
- # v1.9.1: Add content block for branching node
- # v1.9.1: Add content block for target
- ## ALGORITHM: Full Presentation
- # Step 1: Identify points of interest
- # Step 2: Build main path
- # Step 3: Add context
- # Step 4: Score and truncate
- # Step 5: Filter links
- # Format output
- ## Section Filtering by Intention
- ## ALGORITHM: Render Cluster (v1.9.2)
- # Build tree from path (start → focus)
- # Content block
- # Link to next
- # First node - unfold with full prose
- # Link → target unfolding
- # Quote content
- ## Related Documents

**Code refs:**
- `runtime/physics/__init__.py`
- `runtime/physics/cluster_presentation.py`
- `runtime/physics/synthesis_unfold.py`
- `runtime/tests/test_cluster_presentation.py`

**Sections:**
- # Cluster Presentation Implementation
- ## Overview
- ## File Locations
- ## Core Classes
- # runtime/physics/cluster_presentation.py
- # runtime/physics/synthesis_unfold.py
- ## Key Functions
- ## Integration with ExplorationRunner
- # Run exploration
- # Convert to raw cluster
- # Present
- ## Markdown Output Format
- ## Language Support
- # French (default)
- # English
- ## Test Coverage
- ## Related Documents

**Sections:**
- # Cluster Presentation Patterns
- ## Overview
- ## P1: Query vs Intention Drives Presentation
- ## P2: Cluster Has Structure
- ## P3: Markers Signal Structure
- ## P4: Synthesis Unfolds From Floats
- ## P5: Filtering Reduces 200 Nodes to 30
- ## P6: Stats Show What's Hidden
- ## Related Documents

**Sections:**
- # Graph — Algorithm: Energy Flow
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: graph_tick
- ## Per-Tick Processing
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS
- ## Step 1: Compute Character Energies
- # Relationship intensity: how much player cares
- # Geographical proximity
- ## Step 2: Flow Energy Into Narratives
- ## Step 3: Propagate Between Narratives
- # Link type factors — each type has its own propagation strength
- # Collect all transfers first (avoid order dependency)
- # Bidirectional: contradiction heats both sides
- # Reverse direction handled when processing from target
- # Bidirectional: allies rise together
- # Unidirectional: general → specific
- # Unidirectional: specific → general
- # Draining: old loses, new gains
- # Apply transfers
- # Apply drains (supersession)
- ## Step 4: Decay Energy
- # Dynamic — adjusted by criticality feedback
- # Apply decay
- # Floor at minimum
- # Skip recently active
- # Core narratives decay slower
- # Focused narratives decay slower
- # System too cold — let it heat
- # System too hot — dampen
- # Clamp to sane range
- # NEVER DYNAMICALLY ADJUST:
- # - breaking_point (changes story meaning)
- # - belief_flow_rate (changes character importance)
- # - link propagation factors (changes story structure)
- ## Step 5: Recompute Weights
- # Clamp and apply focus evolution
- # Direct: player believes it
- # Indirect: about someone player knows
- # Distant: no direct connection
- # Bonus is limited by weaker of the two
- ## Step 6: Tick Pressures
- # Check for flip
- # Tick gradual component
- # Find scheduled floor
- # Use higher of ticked or floor
- ## Step 7: Detect Flips
- ## Full Tick
- # 1. Character energies (relationship × proximity)
- # 2. Flow into narratives (characters pump)
- # 3. Propagate between narratives (link-type dependent)
- # 4. Decay
- # 5. Check conservation (soft global constraint)
- # 6. Adjust criticality (dynamic decay_rate)
- # 7. Weight recomputation
- # 8. Pressure ticks
- # 9. Detect flips
- ## Automatic Tension from Approach
- # Edmund's energy as player approaches York
- # Day 1 (one day travel):
- # Edmund: intensity=4.0, proximity=0.2 → energy=0.8
- # Day 2 (same region):
- # Edmund: intensity=4.0, proximity=0.7 → energy=2.8
- # No one decided this. Physics decided this.
- # Confrontation pressure rises because Edmund's narratives heat up.
- ## Parameters Summary
- ## Link Type Factors
- ## Conservation Parameters
- ## Never Adjust Dynamically
- ## CHAIN

**Sections:**
- # Graph — Behaviors: What Should Happen
- ## CHAIN
- ## Overview
- ## BEHAVIORS
- ## Behavior: Companions Matter More
- ## Behavior: Contradictions Intensify Together
- ## Behavior: Support Clusters Rise and Fall Together
- ## Behavior: Old Truths Fade When Replaced
- ## Behavior: Core Oaths Persist
- ## Behavior: Pressure Builds Toward Breaking
- ## Behavior: Cascades Ripple Through
- ## Behavior: System Stays Near Criticality
- ## Behavior: Agents Update Links, Not Energy
- ## Summary: What To Expect
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # Graph — Objectives
- ## CHAIN
- ## PURPOSE
- ## OBJECTIVES
- ## OBJECTIVE CONFLICTS
- ## NON-OBJECTIVES
- ## THE CORE INSIGHT
- ## VERIFICATION

**Code refs:**
- `runtime/physics/tick.py`

**Doc refs:**
- `docs/schema/SCHEMA_Moments.md`

**Sections:**
- # Graph — Patterns: Why This Shape
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## The Core Insight
- ## Energy As Attention
- ## Computed, Not Declared
- ## Pressure Requires Release
- ## The Graph Breathes
- ## Criticality
- ## What Agents Never Do
- ## MARKERS

**Code refs:**
- `graph_ops.py`
- `graph_ops_events.py`
- `graph_ops_types.py`
- `orchestrator.py`
- `runtime/infrastructure/api/app.py`
- `runtime/infrastructure/canon/canon_holder.py`
- `runtime/infrastructure/orchestration/narrator.py`
- `runtime/infrastructure/orchestration/orchestrator.py`
- `runtime/infrastructure/orchestration/world_runner.py`
- `runtime/physics/graph/graph_interface.py`
- `runtime/physics/graph/graph_ops_events.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_ops_types.py`
- `runtime/physics/graph/graph_queries_moments.py`
- `runtime/physics/tick.py`
- `tick.py`

**Doc refs:**
- `docs/physics/ALGORITHM_Physics.md`
- `docs/physics/IMPLEMENTATION_Physics.md`
- `docs/physics/graph/BEHAVIORS_Graph.md`
- `docs/physics/graph/SYNC_Graph.md`

**Sections:**
- # Graph — Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## What Exists ✓
- ## Two Paths (Both Valid)
- ## Known False Positives
- ## CONFLICTS
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## CHAIN
- ## Agent Observations
- ## Agent Observations
- ## Agent Observations
- ## ARCHIVE
- ## ARCHIVE
- ## ARCHIVE

**Code refs:**
- `graph_ops.py`
- `runtime/graph/health/check_health.py`
- `runtime/infrastructure/api/app.py`
- `runtime/infrastructure/orchestration/orchestrator.py`
- `runtime/physics/graph/connectome_read_cli.py`
- `runtime/physics/graph/graph_interface.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_ops_events.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_ops_types.py`
- `runtime/physics/graph/graph_queries_moments.py`
- `runtime/physics/graph/graph_queries_search.py`
- `runtime/physics/graph/graph_query_utils.py`

**Doc refs:**
- `docs/physics/graph/ALGORITHM_Energy_Flow.md`
- `docs/physics/graph/ALGORITHM_Weight.md`
- `docs/physics/graph/BEHAVIORS_Graph.md`
- `docs/physics/graph/PATTERNS_Graph.md`
- `docs/physics/graph/SYNC_Graph.md`
- `docs/physics/graph/SYNC_Graph_archive_2025-12.md`
- `docs/physics/graph/VALIDATION_Living_Graph.md`

**Sections:**
- # Archived: SYNC_Graph.md
- ## Maturity
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## Key Design Decisions
- ## The Full Energy Cycle
- ## Next Steps
- ## CONFLICTS
- # Archived: SYNC_Graph.md
- ## Key Design Decisions
- ## The Full Energy Cycle
- ## Next Steps
- ## CONFLICTS
- # Archived: SYNC_Graph.md
- ## Key Design Decisions
- ## The Full Energy Cycle
- ## Next Steps
- ## CONFLICTS
- ## Agent Observations
- # Archived: SYNC_Graph.md
- ## Key Design Decisions
- ## The Full Energy Cycle
- ## Next Steps
- ## CONFLICTS
- ## Agent Observations
- # Archived: SYNC_Graph.md
- ## What's Missing: ONE ENDPOINT
- # TODO: SSE streaming version
- ## RECENT CHANGES
- # Archived: SYNC_Graph.md
- ## RECENT CHANGES
- # Archived: SYNC_Graph.md
- ## RECENT CHANGES

**Doc refs:**
- `docs/physics/graph/SYNC_Graph.md`

**Sections:**
- # THE BLOOD LEDGER — Validation Specification
- # Version: 1.0
- # =============================================================================
- # PURPOSE
- # =============================================================================
- # =============================================================================
- # CHAIN
- # =============================================================================
- ## CHAIN
- # =============================================================================
- # INVARIANTS
- # =============================================================================
- ## INVARIANTS
- # =============================================================================
- # PROPERTIES
- # =============================================================================
- ## PROPERTIES
- # =============================================================================
- # ERROR CONDITIONS
- # =============================================================================
- ## ERROR CONDITIONS
- # =============================================================================
- # TEST COVERAGE
- # =============================================================================
- ## TEST COVERAGE
- # =============================================================================
- # VERIFICATION PROCEDURE
- # =============================================================================
- ## VERIFICATION PROCEDURE
- # =============================================================================
- # SYNC STATUS
- # =============================================================================
- ## SYNC STATUS
- # =============================================================================
- # GRAPH INTEGRITY RULES
- # =============================================================================
- # No links — char_wulfric would be orphaned
- # result.persisted = ["char_aldric", "narr_oath", "link_belief_1"]
- # result.rejected = [
- # {"item": "char_wulfric", "error": "orphaned_node", "fix": "Add link..."}
- # ]
- # =============================================================================
- # VISION MAPPING
- # =============================================================================
- # --- COVERED BY ENERGY SYSTEM ---
- # --- REQUIRES NARRATOR/CONTENT ---
- # =============================================================================
- # EXPECTED BEHAVIORS
- # =============================================================================
- # ---------------------------------------------------------------------------
- # PRESENCE & PROXIMITY
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # LIVING WORLD
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # NARRATIVE TENSION
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # COMPANION DEPTH
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # SYSTEM HEALTH
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # TIME & PRESSURE
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # ENGAGEMENT
- # ---------------------------------------------------------------------------
- # =============================================================================
- # ANTI-PATTERNS
- # =============================================================================
- # =============================================================================
- # TEST SUITE
- # =============================================================================
- # ---------------------------------------------------------------------------
- # PRESENCE & PROXIMITY
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # LIVING WORLD
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # NARRATIVE TENSION
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # COMPANION DEPTH
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # SYSTEM HEALTH
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # TIME & PRESSURE
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # ENGAGEMENT
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # CRITICALITY
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # CASCADE
- # ---------------------------------------------------------------------------
- # ---------------------------------------------------------------------------
- # ANTI-PATTERNS
- # ---------------------------------------------------------------------------
- # =============================================================================
- # SUMMARY
- # =============================================================================
- ## MARKERS

**Sections:**
- # MECHANISMS — Attention Energy Split (v0)
- ## CHAIN
- ## PURPOSE
- ## INPUTS (REQUIRED)
- ## STEP 1 — Build Player Neighborhood
- ## STEP 2 — Enumerate Eligible Sinks
- ## STEP 3 — Compute Sink Mass (Node↔Link Jointure)
- ## STEP 4 — Allocate Attention
- ## STEP 5 — Update Moment Energies (and only moment energies)
- ## OUTPUTS
- ## INTERRUPT COUPLING (uses separate pattern)
- ## FAILURE MODES
- ## VALIDATION HOOKS

**Code refs:**
- `runtime/physics/subentity.py`

**Sections:**
- # MECHANISMS — Awareness Depth + Breadth (v1)
- ## CHAIN
- ## PURPOSE
- ## THE INSIGHT
- ## INPUTS (REQUIRED)
- ## STEP 1 — Classify Link and Update Depth
- # UP: toward abstraction
- # DOWN: toward details
- # else: PEER link, no depth change
- ## STEP 2 — Track Progress Toward Intention
- ## STEP 3 — Detect Fatigue (Stopping Condition)
- ## STEP 4 — Child Crystallization Rule
- # Don't crystallize if we found exactly what we were looking for
- ## STEP 5 — No Parent Propagation
- # OLD (removed):
- # parent.found_narratives.update(child.found_narratives)
- # parent.satisfaction = max(parent.satisfaction, child.satisfaction)
- # NEW:
- # Parent continues its own exploration
- ## OUTPUTS
- ## KEY FORMULAS
- ## FAILURE MODES
- ## ANTI-PATTERNS (What Doesn't Work)
- ## VALIDATION HOOKS
- ## IMPLEMENTATION STATUS

**Sections:**
- # MECHANISMS — Contradiction Pressure (v0)
- ## CHAIN
- ## PURPOSE
- ## INPUTS
- ## EDGE PRESSURE
- ## EFFECT (INDIRECT ONLY)
- ## BEHAVIORAL EXPECTATIONS
- ## FAILURE MODES
- ## VALIDATION HOOKS

**Sections:**
- # MECHANISMS — PRIMES Lag + Half-Life (v0)
- ## CHAIN
- ## PURPOSE
- ## PRIMES LINK FIELDS (REQUIRED)
- ## INPUTS
- ## PRIME EFFECT FUNCTION
- ## HOW PRIMES IS USED (v0)
- ## FAILURE MODES
- ## VALIDATION HOOKS

**Sections:**
- # Nature — Algorithm
- ## CHAIN
- ## CORE ALGORITHM
- # Step 1: Normalize
- # Step 2: Split on comma for post-modifiers
- # Step 3: Find verb (longest match first)
- # Step 4: Extract pre-modifiers
- # Start with defaults
- # Layer 1: Apply verb
- # Layer 2: Apply pre-modifiers
- # Layer 3: Apply post-modifiers
- # Layer 4: Check weight annotations
- # intensity: -1 (attenuated) to +1 (intensified)
- # Combine permanence and energy into intensity
- ## DATA STRUCTURES
- # ↑ attenuated  ↑ intensified
- ## COMPLEXITY

**Sections:**
- # Nature — Behaviors
- ## CHAIN
- ## OBSERVABLE BEHAVIORS
- # Nature Reference
- # nature.yaml re-read on next access
- ## EDGE CASES

**Sections:**
- # Nature — Health
- ## CHAIN
- ## PURPOSE
- ## INDICATORS
- ## HEALTH CHECK IMPLEMENTATION
- # H1: YAML Load
- # H2: Verb Coverage
- # H3: Translation Completeness
- ## GAPS

**Sections:**
- # Nature — Implementation
- ## CHAIN
- ## FILE STRUCTURE
- ## CODE ARCHITECTURE
- # Defaults
- # Verb categories
- # Modifiers
- # Variations
- ## DATA FLOW
- ## DEPENDENCIES
- ## USAGE EXAMPLES
- # Include in agent prompt
- # After editing nature_physics.yaml
- ## EXTENSION POINTS
- # In grammar_verbs:
- # In pre_modifiers:
- # In post_modifiers:

**Sections:**
- # Nature — Objectives
- ## CHAIN
- ## PURPOSE
- ## OBJECTIVES
- ## NON-OBJECTIVES
- ## SUCCESS METRICS

**Code refs:**
- `nature.py`

**Sections:**
- # Nature — Patterns
- ## CHAIN
- ## DESIGN PHILOSOPHY
- ## SCOPE
- ## KEY PATTERNS
- # "acts on" should match "acts on", not "acts"
- # conflicts = [{'key': 'permanence', 'previous': 0.9, 'new': 0.1, 'from': 'perhaps'}]
- ## ANTI-PATTERNS

**Code refs:**
- `runtime/physics/nature.py`

**Sections:**
- # Nature — Sync
- ## CHAIN
- ## CURRENT STATE
- ## RECENT CHANGES
- ## VERB CATEGORIES
- ## MODIFIER COUNTS
- ## NEXT STEPS
- ## BLOCKERS
- ## HANDOFF
- ## ARCHIVE

**Sections:**
- # Archived: SYNC_Nature.md
- ## PROPOSITIONS
- # Au lieu de:
- # Utiliser:
- # Link decay: affecte la force de la relation
- # Node decay: affecte l'énergie du node
- # États de workflow
- # Importance

**Sections:**
- # Nature — Validation
- ## CHAIN
- ## INVARIANTS
- # 'definitely' sets permanence=0.9, 'perhaps' overrides to 0.1
- # "acts on" should not match just "acts"
- # "is linked to" should not match just "is"
- ## TEST COVERAGE
- ## EDGE CASE TESTS
- # No valid verb, modifiers ignored

**Sections:**
- # SubEntity — Algorithm
- ## CHAIN
- ## OVERVIEW
- ## STATE MACHINE
- ## ALGORITHM: Exploration Runner
- # v2.1: Removed intention_type param - intention is semantic via embedding
- ## ALGORITHM: SEEKING
- # Query alignment (WHAT we're searching for)
- # Intention alignment (WHY we're searching)
- # Combined alignment (v2.1: fixed weight, intention is semantic via embedding)
- # = 0.75 * query_alignment + 0.25 * intention_alignment
- # Self-novelty (avoid backtracking)
- # Sibling divergence (spread exploration)
- # Permanence factor (prefer explorable links)
- # Final score
- ## ALGORITHM: BRANCHING
- # Each child now has sibling_ids pointing to its siblings
- ## ALGORITHM: ABSORBING (v1.9)
- ## ALGORITHM: RESONATING
- ## ALGORITHM: REFLECTING (v2.1)
- # v2.1: Only backprop color if the path was useful
- # Path led to good findings - color it
- # Path wasn't useful - don't color (will crystallize instead)
- # Fetch all path links
- # Backprop with intention embedding
- # Save colored links back to graph
- ## ALGORITHM: CRYSTALLIZING
- # spawn_node → new_narrative
- # new_narrative → focus_node
- # v2.1: Color path after crystallization - path led to new knowledge
- # Color with crystallization embedding (what we created)
- # v2.0.1: Always MERGING after crystallizing (avoids loop)
- ## ALGORITHM: MERGING
- # Child crystallizes if needed (v2.0)
- # NO propagation to parent — graph is source of truth
- ## ALGORITHM: Awareness Tracking (v2.0)
- # PEER links (|hierarchy| <= 0.2) don't affect depth
- # In state loop:
- ## KEY FORMULAS
- ## COMPLEXITY

**Sections:**
- # SubEntity — Behaviors
- ## CHAIN
- ## PURPOSE
- ## BEHAVIORS
- ## ANTI-BEHAVIORS
- ## EDGE CASES
- ## INPUTS
- ## OUTPUTS
- ## OBJECTIVES COVERAGE

**Sections:**
- # SubEntity — Health
- ## CHAIN
- ## PURPOSE
- ## WHEN TO USE HEALTH VS TESTS
- ## HEALTH INDICATORS
- ## LOG TRAVERSAL ANALYSIS
- ## HEALTH CHECK FLOW
- ## MANUAL REVIEW CHECKLIST
- ## Exploration Quality Review: {exploration_id}
- ## DOCKING POINTS
- ## HEALTH CHECKER INDEX
- ## HOW TO RUN
- # Run health checks on specific exploration
- # Run on all recent explorations
- ## DIAGNOSTIC REPORTS
- # Diagnostic Report: {exploration_id}
- ## Context
- ## Metrics Summary
- ## Layer Analysis
- ## Detected Patterns
- ## Root Cause
- ## Proposed Improvements
- ## Follow-up Actions
- # Exploration context (logged at START)
- # Termination (logged at END)
- # Branching events (logged when spawning children)
- # Merge events (logged when receiving child results)
- # Link score breakdown (per candidate)
- # Energy injection (per step)
- ## KNOWN GAPS
- ## EXAMPLE: Annotated Health Report

**Sections:**
- # SubEntity — Implementation
- ## CHAIN
- ## CODE STRUCTURE
- ## FILE RESPONSIBILITIES
- ## DESIGN PATTERNS
- # Normalize inputs, register with context, return
- ## ENTRY POINTS
- ## DATA FLOW
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- # runtime/physics/subentity.py:1
- ## TESTS
- ## DEPENDENCIES

**Sections:**
- # SubEntity — Objectives
- ## CHAIN
- ## PURPOSE
- ## PRIMARY OBJECTIVES (Ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS
- ## SUCCESS METRICS

**Code refs:**
- `runtime/physics/cluster_presentation.py`
- `runtime/physics/crystallization.py`
- `runtime/physics/flow.py`
- `runtime/physics/link_scoring.py`
- `runtime/physics/subentity.py`
- `runtime/physics/traversal_logger.py`

**Doc refs:**
- `docs/physics/mechanisms/MECHANISMS_Awareness_Depth_Breadth.md`

**Sections:**
- # SubEntity — Patterns
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## DESIGN PRINCIPLES
- ## SCOPE
- ## INSPIRATIONS
- ## DEPENDENCIES

**Code refs:**
- `runtime/physics/subentity.py`
- `runtime/tests/test_subentity.py`

**Sections:**
- # SubEntity — Sync
- ## CHAIN
- ## HEALTH STATUS
- ## KNOWN ISSUES
- ## HANDOFFS
- ## DOCUMENTATION STATUS
- ## HANDOFF — v2.0 Implementation (COMPLETED)
- ## ARCHIVE
- ## ARCHIVE

**Code refs:**
- `runtime/physics/cluster_presentation.py`
- `runtime/physics/exploration.py`
- `runtime/physics/health/check_subentity.py`
- `runtime/physics/subentity.py`
- `runtime/tests/test_subentity.py`

**Doc refs:**
- `docs/physics/mechanisms/MECHANISMS_Awareness_Depth_Breadth.md`

**Sections:**
- # Archived: SYNC_SubEntity.md
- ## MATURITY
- ## RECENT CHANGES
- ## CODE STATUS
- ## DEPENDENCIES
- ## VERIFICATION COMMANDS
- # Run unit tests
- # Run traversal logger tests
- # Run health validation tests
- # Check specific exploration
- # Check all recent explorations
- # Archived: SYNC_SubEntity.md
- ## INVARIANT STATUS
- ## NEXT ACTIONS
- ## v2.1 — Semantic Intention + Backprop Coloring (2025-12-29)
- # _step_seeking
- # _step_reflecting (if satisfaction > 0.5)
- # _step_crystallizing (after creating narrative)
- ## Bug Fixes: v2.0.1 — Crystallization Loop (2025-12-29)

**Code refs:**
- `runtime/tests/test_subentity.py`
- `runtime/tests/test_traversal_logger.py`

**Sections:**
- # SubEntity — Validation
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- # Parent-child consistency
- # Sibling consistency
- # No circular refs (parent chain should terminate)
- # Energy should have increased by approximately expected amount
- # (tolerance for concurrent updates)
- # Check crystallization rule
- # Should NOT crystallize
- # Should crystallize
- # Verify it's in graph
- # No findings = should crystallize
- # Parent should NOT have inherited child findings (v2.0)
- # Could be coincidence (parent found same thing)
- # But if alignment is identical, it's propagation
- # Should have raised ExplorationTimeoutError
- # If we got a result, timeout wasn't enforced
- # Monotonicity
- # Check increment matches link hierarchy
- # Should have increased depth[0]
- # Should have increased depth[1]
- # Can't be fatigued yet
- ## PRIORITY TABLE
- ## INVARIANT INDEX
- ## VERIFICATION PROCEDURE

**Sections:**
- # Tick Runner — Patterns: Why This Shape
- ## The Core Insight
- ## THE PROBLEM
- ## THE PATTERN
- ## COMPARISON WITH WORLD RUNNER
- ## CLI USAGE
- # Run until any moment completes
- # Run until completion or interruption
- # With options
- # JSON output for scripting
- ## EXIT CODES
- ## INTEGRATION WITH HEALTH
- ## CHAIN

**Code refs:**
- `runtime/physics/subentity.py`
- `runtime/physics/traversal_logger.py`
- `runtime/tests/test_traversal_logger.py`

**Doc refs:**
- `docs/physics/DESIGN_Traversal_Logger.md`
- `docs/physics/EXAMPLE_Traversal_Log.md`

**Sections:**
- # TraversalLogger Implementation
- ## PURPOSE
- ## CODE LOCATIONS
- ## DATA CLASSES
- # Score components
- # Agent-comprehensible additions
- # Agent-comprehensible additions
- ## HELPER CLASSES
- ## LOGGER API
- # Generate descriptive exploration ID
- # Result: exp_edmund_find_truth_about_betrayal_20251226_143052
- # Format: exp_{actor}_{query_slug}_{YYYYMMDD}_{HHMMSS}
- # Or use factory
- # Or use singleton
- # Start exploration
- # Log each step
- # ... all other fields
- # End exploration
- # Log branch
- # Log merge
- # Log crystallize
- ## OUTPUT FILES
- ## LOG LEVELS
- ## INTEGRATION
- # In SubEntity exploration runner
- ## AGENT-COMPREHENSIBLE FEATURES
- ## LINKS

**Code refs:**
- `runtime/physics/traversal_logger.py`
- `runtime/tests/test_traversal_logger.py`

**Doc refs:**
- `docs/physics/DESIGN_Traversal_Logger.md`
- `docs/physics/EXAMPLE_Traversal_Log.md`
- `docs/physics/traversal_logger/IMPLEMENTATION_Traversal_Logger.md`

**Sections:**
- # TraversalLogger — SYNC
- ## CURRENT STATE
- ## IMPLEMENTATION STATUS
- ## FILES
- ## WHAT'S WORKING
- ## NOT IMPLEMENTED (BY DESIGN)
- ## INTEGRATION STATUS
- ## NEXT STEPS
- ## LAST CHANGES

**Code refs:**
- `runtime/physics/exploration.py`

**Doc refs:**
- `algorithms/ALGORITHM_Physics_Energy_Flow_Sources_Sinks_And_Moment_Dynamics.md`
- `algorithms/ALGORITHM_Physics_Energy_Mechanics_And_Link_Semantics.md`
- `algorithms/ALGORITHM_Physics_Handler_And_Input_Processing_Flows.md`
- `algorithms/ALGORITHM_Physics_Mechanisms.md`
- `algorithms/ALGORITHM_Physics_Speed_Control_And_Display_Filtering.md`
- `algorithms/ALGORITHM_Physics_Tick_Cycle_Gating_Flips_And_Dispatch.md`

**Sections:**
- # Physics — Algorithm: System Overview
- ## CHAIN
- ## Consolidation Note
- ## OVERVIEW
- ## DETAILED ALGORITHMS
- ## LEGACY ALGORITHM REDIRECTS
- ## DATA STRUCTURES
- ## ALGORITHM: Physics Tick Cycle
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## ALGORITHM: SubEntity Traversal (v1.8)
- # Intention types and their weights
- # v1.8: Combine query and intention alignment
- # Self-novelty: avoid backtracking (links similar to path)
- # Sibling divergence: avoid siblings' exploration space
- # v1.8: Score links with query+intention alignment, self_novelty, sibling_divergence
- # Only branch on Moments (not other types)
- # Threshold: 2:1 ratio
- # Spawn children with sibling references
- # Update sibling_ids for all children
- # Wait for children, then reflect
- # v1.7.2+: Merge found_narratives dict (max alignment per narrative)
- # v1.8: Compute alignment using both query and intention
- # v1.7.2: found_narratives is dict with max alignment
- # Satisfaction boost weighted by narrative importance
- # Walk path in reverse
- # Attenuation via reverse polarity
- # v1.8: Permanence boost on positive combined alignment
- # v1.8: crystallization_embedding computed at each step with query+intention
- # Check if novel (no similar narrative exists)
- # Create new Narrative
- # Link to found narratives with their alignment scores (v1.7.2: dict)
- # Link to origin Moment
- # v1.7.2: Merge found_narratives dict (max alignment per narrative)
- # Also pass crystallized if we created one
- # Pass to actor
- # Die
- # Energy PASSES THROUGH the link (not stored here)
- # Modified by alignment with intention
- # Modified by hierarchy (containers amplify inward)
- # Link gains weight proportional to flow AND permanence
- # High permanence = solidifies fast
- # Low permanence = stays light
- # Link stores energy proportional to flow AND inverse of permanence
- # High permanence = little energy stored (stable, not reactive)
- # Low permanence = lots of energy stored (volatile, reactive)
- # Energy scales with node weight — heavier nodes get more
- # Only at RESONATING state — no permanence, no convergence bonus
- ## MARKERS

**Code refs:**
- `mind/api/app.py`

**Sections:**
- # Physics — API Reference
- ## CHAIN
- ## Endpoints
- ## Removed Endpoints
- ## Frontend Types
- ## SSE Callbacks
- ## Narrator Output Format
- ## Graph Operations
- # Creation
- # Links
- # Status changes
- # Queries
- # Lifecycle

**Code refs:**
- `runtime/physics/traversal_logger.py`

**Sections:**
- # TraversalLogger Design — SubEntity Exploration Logging
- ## PURPOSE
- ## LOG LEVELS
- ## LOG STRUCTURE
- # For traverse decisions:
- # For branch decisions:
- ## EVENT TYPES
- ## FILE FORMAT
- ## LOG ROTATION
- ## API
- # Exploration lifecycle
- # Step logging
- # Events
- # Query (for analysis)
- ## DATA CLASSES
- ## INTEGRATION POINTS
- # ... existing code
- ## CONFIGURATION
- # .mind/config.yaml
- # What to include at each level
- ## EXAMPLE OUTPUT
- ## NEXT STEPS

**Sections:**
- # Example Traversal Log Output
- ## Scenario
- ## Human-Readable Format
- ## JSONL Format (Machine-Readable)
- ## Index Entry
- ## Query Examples
- # All decisions where sibling_divergence < 0.5
- # All BRANCH events
- # Steps where satisfaction increased
- # Average link score per exploration

**Code refs:**
- `runtime/physics/health/checker.py`

**Sections:**
- # Energy Physics — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## LINK TYPES (Simplified v1.2)
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: energy_balance
- ## INDICATOR: no_negative_energy
- ## INDICATOR: link_hot_cold_ratio
- ## INDICATOR: tick_phase_order
- ## INDICATOR: moment_state_validity
- ## INDICATOR: link_strength_growth
- ## HOW TO RUN
- # Run all health checks for physics
- # Run specific checker
- # Run with verbose output
- # Run continuous monitoring
- ## KNOWN GAPS
- ## VALIDATION IDS REFERENCE
- ## MARKERS

**Code refs:**
- `runtime/physics/cluster_energy_monitor.py`
- `runtime/physics/display_snap_transition_checker.py`
- `runtime/physics/tick.py`

**Sections:**
- # Physics — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- # v1.6.1 SubEntity Exploration Flow
- ## HEALTH INDICATORS SELECTED
- # v1.6.1 SubEntity Exploration Indicators
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- # v1.6.1 SubEntity Checkers
- ## INDICATOR: energy_momentum
- ## TRACE SCENARIOS (VERIFICATION)
- ## CHECK: Snap Display Sequence
- ## CHECK: Cluster Energy Monitor
- ## HOW TO RUN
- # Run physics tests (unit and integration)
- ## NEW HEALTH CHECKS
- ## v1.6.1 SUBENTITY EXPLORATION HEALTH
- ## v1.6.1 KNOWN GAPS

**Code refs:**
- `crystallization.py`
- `exploration.py`
- `flow.py`
- `graph_ops.py`
- `graph_ops_events.py`
- `graph_queries.py`
- `link_scoring.py`
- `phases/completion.py`
- `phases/generation.py`
- `phases/link_cooling.py`
- `phases/moment_draw.py`
- `phases/moment_flow.py`
- `phases/moment_interaction.py`
- `phases/narrative_backflow.py`
- `phases/rejection.py`
- `runtime/infrastructure/api/moments.py`
- `runtime/infrastructure/orchestration/orchestrator.py`
- `runtime/models/links.py`
- `runtime/moment_graph/queries.py`
- `runtime/physics/constants.py`
- `runtime/physics/crystallization.py`
- `runtime/physics/exploration.py`
- `runtime/physics/flow.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_queries_search.py`
- `runtime/physics/graph/graph_query_utils.py`
- `runtime/physics/link_scoring.py`
- `runtime/physics/phases/completion.py`
- `runtime/physics/phases/generation.py`
- `runtime/physics/phases/link_cooling.py`
- `runtime/physics/phases/moment_draw.py`
- `runtime/physics/phases/moment_flow.py`
- `runtime/physics/phases/moment_interaction.py`
- `runtime/physics/phases/narrative_backflow.py`
- `runtime/physics/phases/rejection.py`
- `runtime/physics/subentity.py`
- `runtime/physics/synthesis.py`
- `runtime/physics/tick.py`
- `runtime/physics/tick_v1_2.py`
- `runtime/physics/tick_v1_2_queries.py`
- `runtime/physics/tick_v1_2_types.py`
- `runtime/physics/traversal_logger.py`
- `synthesis.py`

**Doc refs:**
- `algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`
- `docs/physics/PATTERNS_Physics.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Mechanisms.md`

**Sections:**
- # Physics — Implementation: Code Architecture & Runtime
- ## CHAIN
- ## SUMMARY
- ## CODE STRUCTURE & RESPONSIBILITIES
- ## DESIGN & RUNTIME PATTERNS
- ## STATE MANAGEMENT
- ## TICK METABOLISM (FLOWS)
- ## CONCURRENCY, CONFIG & DEPENDENCIES
- ## OBSERVABILITY & LINKS
- ## PHYSICS-BASED SEARCH (v1.2)
- ## SUBENTITY EXPLORATION (v1.8)
- # Start exploration
- # Log each step (called by exploration runner)
- # End exploration
- # Normal mode: returns ExplorationResult only
- # Debug mode: returns ExplorationResult + full traversal logs
- # Output includes:
- # - ExplorationResult (found_narratives, crystallized, satisfaction)
- # - Full JSONL log path
- # - Summary of decisions, anomalies, learning signals
- ## GAPS / PROPOSITIONS

**Doc refs:**
- `docs/schema/SCHEMA_Moments.md`

**Sections:**
- # Physics — Patterns: Why This Shape
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## Core Principle
- ## P1: Potential vs Actual
- ## P2: The Graph Is Alive
- ## P3: Everything Is Moments
- ## P4: Moments Are Specific, Narratives Emerge
- ## P5: Energy Must Land
- ## P6: Sequential Actions, Parallel Potentials
- ## P7: The World Moves Without You
- ## P8: Time Is Elastic
- ## P9: Physics Is The Scheduler
- ## P10: Simultaneous Actions Are Drama
- ## P11: SubEntities Explore With Purpose (v1.8)
- ## P12: No Magic Numbers (v1.6)
- ## P13: Siblings Diverge Naturally (v1.6.1)
- ## P14: Crystallization Is Continuous (v1.8)
- ## P15: Found Narratives Have Alignment (v1.6.1)
- ## P16: Sibling Init via Lazy Refs (v1.6.1)
- ## P17: Branch on Count, Score Handles Selection (v1.6.1)
- ## P18: Link Embedding from Synthesis (v1.6.1)
- ## What This Pattern Does NOT Solve
- ## The Philosophy
- ## MARKERS

**Code refs:**
- `runtime/physics/subentity.py`
- `runtime/physics/traversal_logger.py`
- `runtime/tests/test_traversal_logger.py`

**Doc refs:**
- `docs/physics/ALGORITHM_Physics.md`
- `docs/physics/HEALTH_Energy_Physics.md`
- `docs/physics/VALIDATION_Energy_Physics.md`

**Sections:**
- # Archived: SYNC_Physics.md
- ## MATURITY
- ## v1.6.1 DESIGN OVERVIEW
- # Identity
- # Tree structure
- # Traversal state
- # Intention
- # Accumulated (v1.6.1 refinements)
- ## v1.6.1 DESIGN DECISIONS
- ## v1.6.1 IMPLEMENTATION TODOS
- ## RECENT CHANGES

**Sections:**
- # Energy Physics — Validation: Invariants and Criteria
- ## CHAIN
- ## PURPOSE
- ## LINK TYPE REFERENCE
- # Role property replaces BELIEVES vs ORIGINATED vs witness
- # Emotions + direction replace SUPPORTS vs CONTRADICTS
- ## ENERGY CONSERVATION
- ## LINK STATE INTEGRITY
- ## TICK EXECUTION
- ## MOMENT LIFECYCLE
- ## GENERATION & PROXIMITY
- ## TOP-N FILTER
- ## BACKFLOW GATING
- ## CRYSTALLIZATION
- ## EMOTION HANDLING
- ## VALIDATION ID INDEX
- ## MARKERS

**Code refs:**
- `runtime/connectome/procedure_runner.py`

**Sections:**
- # Procedure — Algorithm: Deterministic Execution Flow
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## What you're doing
- ## Why
- ## How
- ## Watch out
- ## Validation to pass this step
- ## ALGORITHM: start_procedure
- ## ALGORITHM: continue_procedure
- ## ALGORITHM: end_procedure
- ## V1 API (Python)
- # 1. Create Run Space
- # 2. Link to procedure template
- # 3. Get Step 1
- # 4. Link Run Space to Step 1 (active)
- # 5. Link Actor to Run Space
- # Check validation
- # Flip current step (cool down)
- # Heat next step
- ## VALIDATION TYPES (V1)
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## KEY DECISIONS
- ## MARKERS

**Code refs:**
- `runtime/connectome/procedure_runner.py`

**Sections:**
- # Procedure — Behaviors: Observable Execution Effects
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `runtime/health/procedure_health.py`

**Sections:**
- # Procedure — Health: Verification Mechanics and Coverage
- ## WHEN TO USE HEALTH (NOT TESTS)
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: Single Active Step
- ## INDICATOR: Guide Completeness
- ## INDICATOR: Zombie Runs
- ## HOW TO RUN
- # Run all health checks for this module
- # Run a specific checker
- ## KNOWN GAPS
- ## RESOLVED DECISIONS
- # Example: "2025-12-29T10:30:00.000000Z"
- ## MARKERS

**Code refs:**
- `doc_chain.py`
- `persistence.py`
- `procedure_runner.py`
- `runtime/connectome/persistence.py`
- `runtime/connectome/procedure_runner.py`
- `runtime/connectome/schema.py`
- `runtime/connectome/validation.py`

**Sections:**
- # Procedure — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## BIDIRECTIONAL LINKS
- ## RESOLVED DECISIONS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Procedure
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)
- ## MARKERS

**Code refs:**
- `cluster_presentation.py`
- `runtime/connectome/persistence.py`
- `runtime/connectome/procedure_runner.py`
- `runtime/physics/subentity.py`

**Sections:**
- # Procedure — Patterns: Self-Contained Steps with Audit Trail
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## What you're doing
- ## Why
- ## How
- ## Watch out
- ## Validation to pass this step
- ## PRINCIPLES
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## DOC CHAIN IN GRAPH
- ## SCOPE
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## MARKERS

**Code refs:**
- `doc_chain.py`
- `mcp/server.py`
- `runtime/connectome/persistence.py`
- `runtime/connectome/procedure_runner.py`
- `runtime/connectome/schema.py`
- `runtime/connectome/validation.py`
- `runtime/health/procedure_health.py`

**Doc refs:**
- `docs/physics/subentity/SYNC_SubEntity.md`
- `docs/schema/SYNC_Schema.md`

**Sections:**
- # Procedure — SYNC: Current State
- ## CHAIN
- ## CURRENT STATE
- ## HANDOFFS
- ## BLOCKED ON
- ## MARKERS
- ## ARCHIVE

**Code refs:**
- `runtime/connectome/procedure_runner.py`

**Sections:**
- # Archived: SYNC_Procedure.md
- ## MATURITY
- ## RESOLVED DECISIONS
- ## RECENT CHANGES

**Code refs:**
- `runtime/connectome/procedure_runner.py`

**Sections:**
- # Procedure — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## RESOLVED DECISIONS
- ## MARKERS

**Sections:**
- # Procedure — Vocabulary: Terms and Imports
- ## CHAIN
- ## PURPOSE
- ## TERMS
- ## EXECUTORS
- # Agent executor - needs guide
- # Code executor - needs command
- # Actor executor - needs event
- # Hybrid executor - needs both
- ## NARRATIVE SUBTYPES
- ## SKILL IMPORTS
- ## PROCEDURE IMPORTS
- ## SCHEMA MAPPING
- ## MARKERS

**Code refs:**
- `mind/graph/health/check_health.py`

**Sections:**
- # Schema — Algorithm: Schema Loading and Validation Procedures
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: Schema Loading
- ## ALGORITHM: Graph Validation
- # Check required fields
- # Check enum values
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## v1.6.1 ALGORITHM ADDITIONS
- # Polarity is bidirectional array
- # Polarity values in [0, 1]
- # Permanence in [0, 1]
- # Emotions in [-1, +1]
- # Only branch on Moments
- # Valid transitions
- # Check novelty threshold
- # Check path permanence
- # Self-novelty: avoid backtracking
- # Sibling divergence: avoid siblings' exploration space
- # Siblings must share parent
- # Children must have this as parent
- # found_narratives must be tuples
- ## MARKERS

**Sections:**
- # Schema — Behaviors: Observable Effects of Schema Compliance
- ## CHAIN
- ## BEHAVIORS
- ## v1.6.1 SUBENTITY BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # Link Synthesis Grammar
- # Physics → Language Mapping
- ## CHANGELOG v2.1
- ## STRUCTURE
- ## BASE VERBS (from hierarchy + polarity)
- ## PRE-MODIFIERS
- ## TEMPORAL MODIFIERS
- # Recently traversed link
- # Ancient relationship
- # Ongoing moment
- # Brief moment
- ## POST-MODIFIERS
- ## COMBINATION RULES
- ## EXAMPLES
- ## SEMANTIC VERB OVERRIDES
- ## VERB INTENSIFIERS
- ## BIDIRECTIONAL SYNTHESIS
- # Bidirectional link
- ## NARRATIVE CONTEXT MODIFIERS
- # Link to narrative with type: secret
- # Link to narrative with type: mechanism
- # Link between narratives
- # Simplified: "elaborates the pattern from the belief"
- ## NODE SYNTHESIS GRAMMAR
- # Energy state
- # Importance
- # Energy = atmosphere
- # Weight
- # Energy = salience
- # Weight
- # Energy = how contested/active
- # Weight
- # Energy = urgency
- # Status
- ## FULL LINK EXPRESSION
- ## IMPLEMENTATION
- # =============================================================================
- # VOCABULARY (Bilingual: English default, French available)
- # =============================================================================
- # Base verbs
- # Ownership verbs
- # Evidential verbs
- # Spatial verbs
- # Actor verbs
- # Narrative verbs
- # Pre-modifiers
- # Post-modifiers
- # Weight annotations
- # Narrative context
- # Node synthesis
- # Connectors
- # Temporal modifiers
- # Base verbs
- # Ownership verbs
- # Evidential verbs
- # Spatial verbs
- # Actor verbs
- # Narrative verbs
- # Pre-modifiers
- # Post-modifiers
- # Weight annotations
- # Narrative context
- # Node synthesis
- # Connectors
- # Temporal modifiers
- # Intensifier mappings
- # Mutual verb forms for bidirectional links
- # =============================================================================
- # CORE FUNCTIONS
- # =============================================================================
- # === NARRATIVE CONTEXT (if applicable) ===
- # === PRE-MODIFIERS ===
- # Energy
- # Surprise-anticipation
- # Permanence
- # === BASE VERB ===
- # === APPLY INTENSIFIER ===
- # === POST-MODIFIERS ===
- # Fear-anger
- # Trust-disgust
- # Joy-sadness
- # === ASSEMBLE ===
- # Weight annotation
- # Hierarchy-dominant
- # Polarity-dominant
- # === ACTOR OVERRIDES ===
- # === THING OVERRIDES ===
- # === MOMENT OVERRIDES ===
- # === SPACE OVERRIDES ===
- # === NARRATIVE OVERRIDES ===
- # Get mutual form
- # =============================================================================
- # TEMPORAL MODIFIERS (v2.1)
- # =============================================================================
- # Check ongoing/pending status
- # Check duration
- # Try recency first
- # Try staleness for links
- # Try age for notably old/new
- # Try duration for moments
- # =============================================================================
- # NODE SYNTHESIS
- # =============================================================================
- # Energy state
- # Duration modifier (for temporal context)
- # Fall back to status if no duration info
- # =============================================================================
- # FULL EXPRESSION
- # =============================================================================
- # Optionally add temporal context to link
- ## INVARIANTS

**Code refs:**
- `mind/graph/health/check_health.py`

**Sections:**
- # Schema — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## HOW TO USE THIS TEMPLATE
- ## CHAIN
- ## FLOWS ANALYSIS
- # v1.6.1 SubEntity Validation Flow
- ## HEALTH INDICATORS SELECTED
- # v1.6.1 SubEntity Health Indicators
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- # v1.6.1 SubEntity Checkers
- ## INDICATOR: Schema Compliance
- ## HOW TO RUN
- # Run CLI health check
- # Run with JSON output
- # Run pytest suite
- # Run specific test
- ## INDICATOR: SubEntity Integrity (v1.6.1)
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `base.py`
- `check_health.py`
- `nodes.py`
- `runtime/graph/health/check_health.py`
- `runtime/graph/health/test_schema.py`
- `runtime/models/base.py`
- `runtime/models/links.py`
- `runtime/models/nodes.py`
- `test_schema.py`
- `test_schema_links.py`
- `test_schema_nodes.py`

**Sections:**
- # Schema — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## BIDIRECTIONAL LINKS
- ## EXTRACTION CANDIDATES
- ## MARKERS

**Code refs:**
- `check_health.py`

**Sections:**
- # OBJECTIVES — Schema
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)
- ## MARKERS

**Code refs:**
- `runtime/doctor_graph.py`

**Sections:**
- # Schema Design Patterns
- ## Core Philosophy
- ## Key Decisions
- # Nodes
- # Links
- ## What's NOT in the Schema
- ## Invariants

**Code refs:**
- `runtime/doctor_graph.py`
- `runtime/models/links.py`
- `runtime/models/nodes.py`
- `runtime/physics/cluster_presentation.py`

**Doc refs:**
- `docs/schema/GRAMMAR_Link_Synthesis.md`
- `docs/schema/PATTERNS_Schema.md`
- `docs/schema/SYNC_Schema.md`

**Sections:**
- # Schema — Sync: Current State
- ## CURRENT STATE
- ## FILES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## ARCHIVE
- ## ARCHIVE

**Sections:**
- # Archived: SYNC_Schema.md
- ## MATURITY
- ## v1.2 CHANGES SUMMARY
- # Old: Actor -[BELIEVES]-> Narrative
- # New:
- # Old: Actor -[OWES]-> Actor
- # New:
- # Old: Narrative -[SUPPORTS]-> Narrative
- # New:
- ## v1.1 CHANGES SUMMARY
- # All links have emotions (unified list, colored by energy flow)
- ## ESCALATIONS
- ## TODOS
- # Archived: SYNC_Schema.md
- ## KEY CONCEPTS (v1.6.1)
- # Identity
- # Tree structure
- # Traversal state
- # Intention
- # Accumulated findings
- # Updated EVERY traversal step, not just at crystallization
- ## v1.6.1 DESIGN DECISIONS
- ## v1.6.1 IMPLEMENTATION TODOS
- ## v1.5 IMPLEMENTATION TODOS (Still Pending)
- ## OPEN QUESTIONS (v1.6 Escalations)

**Code refs:**
- `check_health.py`
- `mind/graph/health/check_health.py`

**Sections:**
- # Schema — Validation: Invariants and Verification
- ## CHAIN
- ## BEHAVIORS GUARANTEED
- ## OBJECTIVES COVERED
- ## INVARIANTS
- ## v1.6 INVARIANTS (NEW)
- # Siblings resolved via lazy refs (sibling_ids + ExplorationContext)
- ## DETAILED COVERAGE TABLES
- # Query source node type
- # Query target node type
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # Run all schema tests
- # Run health check
- # Check for mutations (should find none)
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # Tools — Algorithm: Script Flow
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: stream_dialogue.main
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS
- ## FLOWS

**Sections:**
- # Tools — Behaviors: Utility Outcomes
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Doc refs:**
- `docs/tools/HEALTH_Tools.md`
- `docs/tools/OBJECTIVES_Tools_Goals.md`

**Sections:**
- # Tools — Health: Verification
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## HOW TO USE THIS TEMPLATE
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## DOCK TYPES (COMPLETE LIST)
- ## CHECKER INDEX
- ## INDICATOR: tool_doc_completeness
- ## INDICATOR: tool_execution_consistency
- ## HEALTH CHECKS
- ## HOW TO RUN
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `stream_dialogue.py`
- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `tools/stream_dialogue.py`

**Sections:**
- # Tools — Implementation: Code Mapping
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## CODE LOCATIONS
- ## MARKERS
- ## CODE LOCATIONS

**Sections:**
- # OBJECTIVES — Tools
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `stream_dialogue.py`
- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `tools/stream_dialogue.py`

**Sections:**
- # Tools — Patterns: Utility Scripts
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `tools/stream_dialogue.py`

**Doc refs:**
- `docs/runtime/membrane/PATTERN_Membrane_Modulation.md`
- `docs/tools/ALGORITHM_Tools.md`
- `docs/tools/BEHAVIORS_Tools.md`
- `docs/tools/HEALTH_Tools.md`
- `docs/tools/IMPLEMENTATION_Tools.md`
- `docs/tools/PATTERNS_Tools.md`
- `docs/tools/SYNC_Tools.md`
- `docs/tools/VALIDATION_Tools.md`

**Sections:**
- # Tools — Sync: Current State
- ## CHAIN
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## KNOWN ISSUES
- ## RECENT CHANGES
- ## Agent Observations
- ## TODO
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## POINTERS
- ## CONSCIOUSNESS TRACE

**Code refs:**
- `tools/stream_dialogue.py`

**Doc refs:**
- `tools/HEALTH_Tools.md`

**Sections:**
- # Tools — Validation: Invariants
- ## CHAIN
- ## BEHAVIORS GUARANTEED
- ## OBJECTIVES COVERED
- ## INVARIANTS
- ## PROPERTIES
- ## ERROR CONDITIONS
- ## HEALTH COVERAGE
- ## VERIFICATION PROCEDURE
- # None of these scripts currently ship automated tests; run them manually when making doc changes.
- ## SYNC STATUS
- ## MARKERS

**Sections:**
- # mind-mcp Architecture
- ## Layer Position: L1 (Citizen)
- ## Core Responsibilities
- ## Key Design Decisions
- ## Module Structure
- ## Data Flow
- ## Related Repos

**Code refs:**
- `Next.js`
- `Node.js`
- `__init__.py`
- `__main__.py`
- `adapter.py`
- `agent_cli.py`
- `agents/handler.py`
- `agents/prompts.py`
- `agents/response.py`
- `app.py`
- `app/api/connectome/tick/route.ts`
- `app/api/sse/route.ts`
- `approval/notifications.py`
- `approval/queue.py`
- `approval/tiers.py`
- `base.py`
- `building/config/mapping.py`
- `building/ingest/create.py`
- `building/ingest/discover.py`
- `building/ingest/parse.py`
- `check_github_for_latest_version.py`
- `check_health.py`
- `check_mind_status_in_directory.py`
- `cli.py`
- `cli/__main__.py`
- `cli/commands/fix_embeddings.py`
- `cli/commands/init.py`
- `cli/commands/status.py`
- `cli/commands/upgrade.py`
- `cli/config.py`
- `cli/helpers/generate_embeddings_for_graph_nodes.py`
- `cli/helpers/ingest_repo_files_to_graph.py`
- `cli/helpers/inject_seed_yaml_to_graph.py`
- `cli/helpers/show_upgrade_notice_if_available.py`
- `cluster_presentation.py`
- `config.py`
- `config/agents.py`
- `config/mapping.py`
- `connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `content/inference.py`
- `content/moment.py`
- `content/narrative.py`
- `context.py`
- `context/format.py`
- `context/query.py`
- `copy_ecosystem_templates_to_target.py`
- `copy_runtime_package_to_target.py`
- `core_utils.py`
- `create_ai_config_files_for_claude_agents_gemini.py`
- `create_database_config_yaml.py`
- `create_env_example_file.py`
- `create_mcp_config_json.py`
- `crystallization.py`
- `deployment/backup.py`
- `deployment/deployer.py`
- `deployment/monitor.py`
- `deployment/rollback.py`
- `diagnosis/evidence.py`
- `diagnosis/layer_attribution.py`
- `diagnosis/pattern_detector.py`
- `diffusion_sim_v2.py`
- `doc_chain.py`
- `doctor.py`
- `doctor_checks.py`
- `doctor_cli_parser_and_run_checker.py`
- `doctor_report.py`
- `engine/connectome/persistence.py`
- `engine/connectome/schema.py`
- `exploration.py`
- `factory.py`
- `falkordb_adapter.py`
- `fix_embeddings_for_nodes_and_links.py`
- `flow.py`
- `frontend/app/scenarios/page.tsx`
- `frontend/app/start/page.tsx`
- `frontend/hooks/useGameState.ts`
- `gemini_agent.py`
- `generate_repo_overview_maps.py`
- `get_mcp_version_from_config.py`
- `get_paths_for_templates_and_runtime.py`
- `graph_interface.py`
- `graph_ops.py`
- `graph_ops_apply.py`
- `graph_ops_events.py`
- `graph_ops_image.py`
- `graph_ops_moments.py`
- `graph_ops_read_only_interface.py`
- `graph_ops_types.py`
- `graph_queries.py`
- `graph_queries_search.py`
- `ingest/__init__.py`
- `ingest/create.py`
- `ingest/discover.py`
- `ingest/markers.py`
- `ingest/parse.py`
- `ingest_repo_files_to_graph.py`
- `inject_seed_yaml_to_graph.py`
- `learning/embeddings.py`
- `learning/extractor.py`
- `learning/pattern_library.py`
- `link_scoring.py`
- `loop.py`
- `mcp/server.py`
- `mind/api/app.py`
- `mind/cli.py`
- `mind/core_utils.py`
- `mind/graph/health/check_health.py`
- `mind/llms/gemini_agent.py`
- `mind/prompt.py`
- `mind/repair.py`
- `mind/repair_verification.py`
- `mind/tests/test_moment.py`
- `mind/validate.py`
- `mock_adapter.py`
- `models.py`
- `moment_processor.py`
- `narrator.py`
- `narrator/prompt_builder.py`
- `nature.py`
- `neo4j_adapter.py`
- `nodes.py`
- `orchestrator.py`
- `persistence.py`
- `phases/completion.py`
- `phases/generation.py`
- `phases/link_cooling.py`
- `phases/moment_draw.py`
- `phases/moment_flow.py`
- `phases/moment_interaction.py`
- `phases/narrative_backflow.py`
- `phases/rejection.py`
- `procedure_runner.py`
- `proposals/generator.py`
- `proposals/scorer.py`
- `proposals/types.py`
- `protocol_runner.py`
- `repair_verification.py`
- `route.ts`
- `runtime/agent_cli.py`
- `runtime/agents/postures.py`
- `runtime/api/app.py`
- `runtime/cli.py`
- `runtime/cluster_builder.py`
- `runtime/cluster_health.py`
- `runtime/cluster_metrics.py`
- `runtime/connectome/persistence.py`
- `runtime/connectome/procedure_runner.py`
- `runtime/connectome/runner.py`
- `runtime/connectome/schema.py`
- `runtime/connectome/session.py`
- `runtime/connectome/steps.py`
- `runtime/connectome/templates.py`
- `runtime/connectome/validation.py`
- `runtime/context.py`
- `runtime/core_utils.py`
- `runtime/doc_extractor.py`
- `runtime/doctor.py`
- `runtime/doctor_checks.py`
- `runtime/doctor_checks_content.py`
- `runtime/doctor_checks_core.py`
- `runtime/doctor_checks_docs.py`
- `runtime/doctor_checks_membrane.py`
- `runtime/doctor_checks_metadata.py`
- `runtime/doctor_checks_naming.py`
- `runtime/doctor_checks_prompt_integrity.py`
- `runtime/doctor_checks_quality.py`
- `runtime/doctor_checks_reference.py`
- `runtime/doctor_checks_stub.py`
- `runtime/doctor_checks_sync.py`
- `runtime/doctor_files.py`
- `runtime/doctor_graph.py`
- `runtime/doctor_report.py`
- `runtime/doctor_types.py`
- `runtime/github.py`
- `runtime/graph/health/check_health.py`
- `runtime/graph/health/lint_terminology.py`
- `runtime/graph/health/test_schema.py`
- `runtime/handlers/base.py`
- `runtime/health/procedure_health.py`
- `runtime/infrastructure/api/app.py`
- `runtime/infrastructure/api/graphs.py`
- `runtime/infrastructure/api/moments.py`
- `runtime/infrastructure/api/playthroughs.py`
- `runtime/infrastructure/api/sse_broadcast.py`
- `runtime/infrastructure/api/tempo.py`
- `runtime/infrastructure/canon/canon_holder.py`
- `runtime/infrastructure/database/__init__.py`
- `runtime/infrastructure/database/adapter.py`
- `runtime/infrastructure/database/factory.py`
- `runtime/infrastructure/database/falkordb_adapter.py`
- `runtime/infrastructure/database/neo4j_adapter.py`
- `runtime/infrastructure/embeddings/service.py`
- `runtime/infrastructure/memory/__init__.py`
- `runtime/infrastructure/memory/moment_processor.py`
- `runtime/infrastructure/memory/transcript.py`
- `runtime/infrastructure/orchestration/agent_cli.py`
- `runtime/infrastructure/orchestration/narrator.py`
- `runtime/infrastructure/orchestration/orchestrator.py`
- `runtime/infrastructure/orchestration/world_runner.py`
- `runtime/infrastructure/tempo/health_check.py`
- `runtime/infrastructure/tempo/tempo_controller.py`
- `runtime/init_cmd.py`
- `runtime/init_db.py`
- `runtime/llms/gemini_agent.py`
- `runtime/llms/tool_helpers.py`
- `runtime/membrane/functions.py`
- `runtime/membrane/health_check.py`
- `runtime/membrane/provider.py`
- `runtime/migrations/migrate_001_schema_alignment.py`
- `runtime/migrations/migrate_temporal_v171.py`
- `runtime/migrations/migrate_tick_to_tick_created.py`
- `runtime/migrations/migrate_to_content_field.py`
- `runtime/migrations/migrate_to_v2_schema.py`
- `runtime/models/__init__.py`
- `runtime/models/base.py`
- `runtime/models/links.py`
- `runtime/models/nodes.py`
- `runtime/moment_graph/__init__.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`
- `runtime/moments/__init__.py`
- `runtime/physics/__init__.py`
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`
- `runtime/physics/cluster_energy_monitor.py`
- `runtime/physics/cluster_presentation.py`
- `runtime/physics/constants.py`
- `runtime/physics/contradiction_pressure_from_negative_polarity_mechanism.py`
- `runtime/physics/crystallization.py`
- `runtime/physics/display_snap_transition_checker.py`
- `runtime/physics/exploration.py`
- `runtime/physics/flow.py`
- `runtime/physics/graph/adapters/__init__.py`
- `runtime/physics/graph/adapters/base.py`
- `runtime/physics/graph/adapters/falkordb_adapter.py`
- `runtime/physics/graph/adapters/mock_adapter.py`
- `runtime/physics/graph/adapters/neo4j_adapter.py`
- `runtime/physics/graph/connectome_read_cli.py`
- `runtime/physics/graph/graph_interface.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_ops_apply.py`
- `runtime/physics/graph/graph_ops_events.py`
- `runtime/physics/graph/graph_ops_links.py`
- `runtime/physics/graph/graph_ops_moments.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_ops_types.py`
- `runtime/physics/graph/graph_queries.py`
- `runtime/physics/graph/graph_queries_moments.py`
- `runtime/physics/graph/graph_queries_search.py`
- `runtime/physics/graph/graph_query_utils.py`
- `runtime/physics/health/check_subentity.py`
- `runtime/physics/health/checker.py`
- `runtime/physics/health/checkers/energy_conservation.py`
- `runtime/physics/health/checkers/moment_lifecycle.py`
- `runtime/physics/link_scoring.py`
- `runtime/physics/nature.py`
- `runtime/physics/phases/completion.py`
- `runtime/physics/phases/generation.py`
- `runtime/physics/phases/link_cooling.py`
- `runtime/physics/phases/moment_draw.py`
- `runtime/physics/phases/moment_flow.py`
- `runtime/physics/phases/moment_interaction.py`
- `runtime/physics/phases/narrative_backflow.py`
- `runtime/physics/phases/rejection.py`
- `runtime/physics/primes_lag_and_half_life_decay_mechanism.py`
- `runtime/physics/subentity.py`
- `runtime/physics/synthesis.py`
- `runtime/physics/synthesis_unfold.py`
- `runtime/physics/tick.py`
- `runtime/physics/tick_v1_2.py`
- `runtime/physics/tick_v1_2_queries.py`
- `runtime/physics/tick_v1_2_types.py`
- `runtime/physics/traversal_logger.py`
- `runtime/project_map.py`
- `runtime/project_map_html.py`
- `runtime/prompt.py`
- `runtime/protocol_runner.py`
- `runtime/protocol_validator.py`
- `runtime/refactor.py`
- `runtime/repair.py`
- `runtime/repair_core.py`
- `runtime/repair_escalation_interactive.py`
- `runtime/repair_instructions.py`
- `runtime/repair_instructions_docs.py`
- `runtime/repair_report.py`
- `runtime/repair_verification.py`
- `runtime/repo_overview.py`
- `runtime/repo_overview_formatters.py`
- `runtime/solve_escalations.py`
- `runtime/symbol_extractor.py`
- `runtime/sync.py`
- `runtime/tests/test_cluster_energy_monitor.py`
- `runtime/tests/test_cluster_presentation.py`
- `runtime/tests/test_e2e_moment_graph.py`
- `runtime/tests/test_energy_v1_2.py`
- `runtime/tests/test_moment.py`
- `runtime/tests/test_moment_graph.py`
- `runtime/tests/test_moment_lifecycle.py`
- `runtime/tests/test_moments_api.py`
- `runtime/tests/test_physics_display_snap.py`
- `runtime/tests/test_router_schema_validation.py`
- `runtime/tests/test_subentity.py`
- `runtime/tests/test_traversal_logger.py`
- `runtime/validate.py`
- `runtime/work.py`
- `scripts/check_chain_links.py`
- `scripts/check_doc_completeness.py`
- `scripts/check_doc_refs.py`
- `scripts/check_orphans.py`
- `semantic_proximity_based_character_node_selector.py`
- `setup_database_and_apply_schema.py`
- `show_upgrade_notice_if_available.py`
- `signals/aggregator.py`
- `signals/collector.py`
- `snake_case.py`
- `stream_dialogue.py`
- `surface.py`
- `sync_skills_to_ai_tool_directories.py`
- `synthesis.py`
- `test_loader.py`
- `test_runner.py`
- `test_schema.py`
- `test_schema_links.py`
- `test_schema_nodes.py`
- `test_session.py`
- `test_steps.py`
- `test_validation.py`
- `tests/building/test_agents.py`
- `tests/building/test_ingest.py`
- `tests/mind/test_cli.py`
- `tests/mind/test_cluster_builder.py`
- `tests/runtime/test_cli.py`
- `tests/runtime/test_cluster_builder.py`
- `tests/test_cluster_stability.py`
- `tick.py`
- `tools/archive/migrate_schema_v11.py`
- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `tools/coverage/validate.py`
- `tools/mcp/membrane_server.py`
- `tools/migrate_v11_fields.py`
- `tools/stream_dialogue.py`
- `tools/test_health_live.py`
- `update_gitignore_with_runtime_entry.py`
- `utils.py`
- `validate_embedding_config_matches_stored.py`
- `validation/modes/shadow.py`
- `validation/modes/unit_test.py`
- `validation/validator.py`

**Doc refs:**
- `agents/narrator/CLAUDE.md`
- `agents/narrator/CLAUDE_old.md`
- `agents/world_runner/CLAUDE.md`
- `algorithms/ALGORITHM_Physics_Energy_Flow_Sources_Sinks_And_Moment_Dynamics.md`
- `algorithms/ALGORITHM_Physics_Energy_Mechanics_And_Link_Semantics.md`
- `algorithms/ALGORITHM_Physics_Handler_And_Input_Processing_Flows.md`
- `algorithms/ALGORITHM_Physics_Mechanisms.md`
- `algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`
- `algorithms/ALGORITHM_Physics_Speed_Control_And_Display_Filtering.md`
- `algorithms/ALGORITHM_Physics_Tick_Cycle_Gating_Flips_And_Dispatch.md`
- `archive/SYNC_CLI_Development_State_archive_2025-12.md`
- `archive/SYNC_archive_2024-12.md`
- `data/ARCHITECTURE — Cybernetic Studio.md`
- `data/MIND Documentation Chain Pattern (Draft “Marco”).md`
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`
- `docs/agents/PATTERNS_Agent_System.md`
- `docs/agents/narrator/ALGORITHM_Scene_Generation.md`
- `docs/agents/narrator/BEHAVIORS_Narrator.md`
- `docs/agents/narrator/HANDOFF_Rolling_Window_Architecture.md`
- `docs/agents/narrator/HEALTH_Narrator.md`
- `docs/agents/narrator/IMPLEMENTATION_Narrator.md`
- `docs/agents/narrator/INPUT_REFERENCE.md`
- `docs/agents/narrator/PATTERNS_Narrator.md`
- `docs/agents/narrator/PATTERNS_World_Building.md`
- `docs/agents/narrator/SYNC_Narrator.md`
- `docs/agents/narrator/SYNC_Narrator_archive_2025-12.md`
- `docs/agents/narrator/TEST_Narrator.md`
- `docs/agents/narrator/TOOL_REFERENCE.md`
- `docs/agents/narrator/VALIDATION_Narrator.md`
- `docs/agents/narrator/archive/SYNC_archive_2024-12.md`
- `docs/architecture/cybernetic_studio_architecture/ALGORITHM_Cybernetic_Studio_Process_Flow.md`
- `docs/architecture/cybernetic_studio_architecture/BEHAVIORS_Cybernetic_Studio_System_Behaviors.md`
- `docs/architecture/cybernetic_studio_architecture/HEALTH_Cybernetic_Studio_Health_Checks.md`
- `docs/architecture/cybernetic_studio_architecture/IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md`
- `docs/architecture/cybernetic_studio_architecture/PATTERNS_Cybernetic_Studio_Architecture.md`
- `docs/architecture/cybernetic_studio_architecture/SYNC_Cybernetic_Studio_Architecture_State.md`
- `docs/architecture/cybernetic_studio_architecture/VALIDATION_Cybernetic_Studio_Architectural_Invariants.md`
- `docs/capabilities/PATTERNS_Capabilities.md`
- `docs/cli/ALGORITHM_CLI_Command_Execution_Logic.md`
- `docs/cli/HEALTH_CLI_Coverage.md`
- `docs/cli/archive/SYNC_CLI_Development_State_archive_2025-12.md`
- `docs/cli/archive/SYNC_CLI_State_Archive_2025-12.md`
- `docs/cli/archive/SYNC_archive_2024-12.md`
- `docs/cli/commands/IMPLEMENTATION_Agents_Command.md`
- `docs/cli/commands/IMPLEMENTATION_Events_Command.md`
- `docs/cli/commands/IMPLEMENTATION_Tasks_Command.md`
- `docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md`
- `docs/cli/core/BEHAVIORS_CLI_Command_Effects.md`
- `docs/cli/core/HEALTH_CLI_Command_Test_Coverage.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/runtime/IMPLEMENTATION_Runtime_And_Dependencies.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/schema/IMPLEMENTATION_Schema.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/structure/IMPLEMENTATION_Code_Structure.md`
- `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`
- `docs/cli/core/SYNC_CLI_Development_State.md`
- `docs/cli/core/VALIDATION_CLI_Instruction_Invariants.md`
- `docs/cli/prompt/ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md`
- `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`
- `docs/cli/prompt/PATTERNS_Prompt_Command_Workflow_Design.md`
- `docs/cli/prompt/SYNC_Prompt_Command_State.md`
- `docs/connectome/PATTERNS_Connectome.md`
- `docs/core_utils/ALGORITHM_Core_Utils_Template_Path_And_Module_Discovery.md`
- `docs/core_utils/ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md`
- `docs/core_utils/PATTERNS_Core_Utils_Functions.md`
- `docs/infrastructure/api/ALGORITHM_Api.md`
- `docs/infrastructure/api/ALGORITHM_Playthrough_Creation.md`
- `docs/infrastructure/api/API_Graph_Management.md`
- `docs/infrastructure/api/BEHAVIORS_Api.md`
- `docs/infrastructure/api/IMPLEMENTATION_Api.md`
- `docs/infrastructure/api/PATTERNS_Api.md`
- `docs/infrastructure/api/SYNC_Api.md`
- `docs/infrastructure/api/TEST_Api.md`
- `docs/infrastructure/api/VALIDATION_Api.md`
- `docs/infrastructure/canon/PATTERNS_Canon.md`
- `docs/infrastructure/tempo/ALGORITHM_Tempo_Controller.md`
- `docs/infrastructure/tempo/IMPLEMENTATION_Tempo.md`
- `docs/infrastructure/tempo/PATTERNS_Tempo.md`
- `docs/ingest/PATTERNS_Doc_Ingestion.md`
- `docs/ingest/PATTERNS_File_Ingestion.md`
- `docs/ingest/PATTERNS_Graph_Injection.md`
- `docs/llm_agents/ALGORITHM_Gemini_Stream_Flow.md`
- `docs/llm_agents/BEHAVIORS_Gemini_Agent_Output.md`
- `docs/llm_agents/HEALTH_LLM_Agent_Coverage.md`
- `docs/llm_agents/IMPLEMENTATION_LLM_Agent_Code_Architecture.md`
- `docs/llm_agents/PATTERNS_Provider_Specific_LLM_Subprocesses.md`
- `docs/llm_agents/SYNC_LLM_Agents_State.md`
- `docs/llm_agents/SYNC_LLM_Agents_State_archive_2025-12.md`
- `docs/llm_agents/VALIDATION_Gemini_Agent_Invariants.md`
- `docs/membrane/IMPLEMENTATION_Membrane_System.md`
- `docs/membrane/VALIDATION_Completion_Verification.md`
- `docs/mind/models/HEALTH_Models.md`
- `docs/mind/models/PATTERNS_Models.md`
- `docs/mind/models/VALIDATION_Models.md`
- `docs/mind_cli_core/OBJECTIVES_mind_cli_core.md`
- `docs/mind_cli_core/PATTERNS_mind_cli_core.md`
- `docs/mind_cli_core/SYNC_mind_cli_core.md`
- `docs/physics/ALGORITHM_Physics.md`
- `docs/physics/BEHAVIORS_Physics.md`
- `docs/physics/DESIGN_Traversal_Logger.md`
- `docs/physics/EXAMPLE_Traversal_Log.md`
- `docs/physics/HEALTH_Energy_Physics.md`
- `docs/physics/IMPLEMENTATION_Physics.md`
- `docs/physics/PATTERNS_Physics.md`
- `docs/physics/SYNC_Physics.md`
- `docs/physics/SYNC_Physics_archive_2025-12.md`
- `docs/physics/TEST_Physics.md`
- `docs/physics/VALIDATION_Energy_Physics.md`
- `docs/physics/VALIDATION_Physics.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Mechanisms.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.1_Energy_Physics.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`
- `docs/physics/attention/PATTERNS_Attention_Energy_Split.md`
- `docs/physics/attention/VALIDATION_Attention_Split_And_Interrupts.md`
- `docs/physics/graph/ALGORITHM_Energy_Flow.md`
- `docs/physics/graph/ALGORITHM_Weight.md`
- `docs/physics/graph/BEHAVIORS_Graph.md`
- `docs/physics/graph/PATTERNS_Graph.md`
- `docs/physics/graph/SYNC_Graph.md`
- `docs/physics/graph/SYNC_Graph_archive_2025-12.md`
- `docs/physics/graph/VALIDATION_Living_Graph.md`
- `docs/physics/mechanisms/MECHANISMS_Awareness_Depth_Breadth.md`
- `docs/physics/subentity/ALGORITHM_SubEntity.md`
- `docs/physics/subentity/BEHAVIORS_SubEntity.md`
- `docs/physics/subentity/SYNC_SubEntity.md`
- `docs/physics/subentity/VALIDATION_SubEntity.md`
- `docs/physics/traversal_logger/IMPLEMENTATION_Traversal_Logger.md`
- `docs/runtime/membrane/BEHAVIORS_Membrane_Modulation.md`
- `docs/runtime/membrane/PATTERNS_Membrane_Modulation.md`
- `docs/runtime/membrane/PATTERNS_Membrane_Scoping.md`
- `docs/runtime/membrane/PATTERN_Membrane_Modulation.md`
- `docs/runtime/membrane/SYNC_Membrane_Modulation.md`
- `docs/runtime/models/HEALTH_Models.md`
- `docs/runtime/models/PATTERNS_Models.md`
- `docs/runtime/models/VALIDATION_Models.md`
- `docs/runtime/moments/PATTERNS_Moments.md`
- `docs/runtime/moments/SYNC_Moments.md`
- `docs/schema/GRAMMAR_Link_Synthesis.md`
- `docs/schema/PATTERNS_Schema.md`
- `docs/schema/SCHEMA.md`
- `docs/schema/SCHEMA_Moments.md`
- `docs/schema/SYNC_Schema.md`
- `docs/schema/models/PATTERNS_Pydantic_Schema_Models.md`
- `docs/tools/ALGORITHM_Tools.md`
- `docs/tools/BEHAVIORS_Tools.md`
- `docs/tools/HEALTH_Tools.md`
- `docs/tools/IMPLEMENTATION_Tools.md`
- `docs/tools/OBJECTIVES_Tools_Goals.md`
- `docs/tools/PATTERNS_Tools.md`
- `docs/tools/SYNC_Tools.md`
- `docs/tools/VALIDATION_Tools.md`
- `implementation/IMPLEMENTATION_Physics_Architecture.md`
- `implementation/IMPLEMENTATION_Physics_Code_Structure.md`
- `implementation/IMPLEMENTATION_Physics_Dataflow.md`
- `implementation/IMPLEMENTATION_Physics_Runtime.md`
- `state/SYNC_Project_State.md`
- `templates/CLAUDE_ADDITION.md`
- `templates/CODEX_SYSTEM_PROMPT_ADDITION.md`
- `templates/mind/PRINCIPLES.md`
- `templates/mind/PROTOCOL.md`
- `templates/mind/agents/manager/CLAUDE.md`
- `templates/runtime/PRINCIPLES.md`
- `templates/runtime/PROTOCOL.md`
- `templates/runtime/agents/manager/CLAUDE.md`
- `tools/HEALTH_Tools.md`

**Sections:**
- # Repository Map: mind-mcp

**Definitions:**
- `class MindServer`
- `def __init__()`
- `def handle_request()`
- `def _handle_initialize()`
- `def _handle_list_tools()`
- `def _handle_call_tool()`
- `def _tool_start()`
- `def _tool_continue()`
- `def _tool_abort()`
- `def _tool_list()`
- `def _tool_agent_list()`
- `def _tool_task_list()`
- `def _tool_agent_run()`
- `def _tool_agent_status()`
- `def _tool_graph_query()`
- `def _resolve_actor()`
- `async def _ask_async()`
- `async def _ask_single()`
- `def _tool_capability_status()`
- `def _tool_capability_trigger()`
- `def _tool_capability_list()`
- `def _tool_file_watcher()`
- `def _tool_git_trigger()`
- `def _tool_task_claim()`
- `def _tool_task_complete()`
- `def _tool_task_fail()`
- `def _tool_agent_heartbeat()`
- `def _format_response()`
- `def _success_response()`
- `def _error_response()`
- `def main()`

**Docs:** `docs/agents/PATTERNS_Agent_System.md`

**Docs:** `docs/agents/PATTERNS_Agent_System.md`

**Definitions:**
- `class AgentCommand`
- `def normalize_agent()`
- `def build_agent_command()`

**Definitions:**
- `def _get_link_physics()`
- `def _build_link_props()`
- `def _link_set_clause()`
- `class AgentInfo`
- `class AgentGraph`
- `def __init__()`
- `def _connect()`
- `def ensure_agents_exist()`
- `def get_all_agents()`
- `def _get_fallback_agents()`
- `def get_available_agents()`
- `def get_running_agents()`
- `def select_agent_for_task()`
- `def get_agent_name()`
- `def set_agent_running()`
- `def set_agent_ready()`
- `def boost_agent_energy()`
- `def set_agent_space()`
- `def link_task_to_space()`
- `def get_task_space()`
- `def get_agent_space()`
- `def link_agent_to_task()`
- `def link_agent_to_problem()`
- `def get_task_task_type()`
- `def create_assignment_moment()`
- `def get_actor_last_moment()`
- `def create_moment()`
- `def link_moments()`
- `def update_agent_cwd()`
- `def assign_agent_to_work()`
- `def upsert_problem_narrative()`
- `def upsert_task_narrative()`
- `def get_agent_template_path()`
- `def load_agent_prompt()`

**Definitions:**
- `class SessionInfo`
- `def get_project_hash()`
- `def path_to_dir_name()`
- `def find_project_sessions_dir()`
- `def get_last_jsonl_timestamp()`
- `def get_session_activity()`
- `def check_agent_liveness()`
- `def get_all_active_agents()`
- `def sync_liveness_to_graph()`
- `def get_active_agent_from_session()`
- `def get_all_active_agents_from_sessions()`
- `def get_session_id_for_agent()`

**Docs:** `docs/agents/PATTERNS_Agent_System.md`

**Definitions:**
- `def make_id()`
- `def discover_agents()`
- `def get_agent_id()`
- `def list_agents()`
- `def get_name_description()`
- `def normalize_agent_id()`
- `def extract_agent_name()`

**Docs:** `docs/agents/PATTERNS_Ag`

**Definitions:**
- `def get_agent_system_prompt()`
- `def get_learnings_content()`
- `def split_docs_to_read()`
- `def _detect_github_issue_number()`
- `def build_agent_prompt()`

**Docs:** `docs/agents/PATTER`

**Definitions:**
- `class RunResult`
- `async def run_work_agent()`
- `class _InternalResult`
- `async def _run_with_retry()`
- `class _ConversationTurn`
- `class _ConversationBatch`
- `class _RunResult`
- `def _detect_cd_commands()`
- `def _group_turns_into_batches()`
- `async def _run_agent()`
- `async def run_for_task()`

**Docs:** `docs/agents/PATTERNS_Agent_System.md`

**Definitions:**
- `class VerificationSession`
- `def record_attempt()`
- `def should_escalate()`
- `def get_escalation_reason()`
- `def mark_escalated()`
- `def add_deferred_todo()`
- `class VerificationCheck`
- `class VerificationResult`
- `def _run_file_check()`
- `def _run_command_check()`
- `def _run_membrane_check()`
- `def _execute_membrane_query()`
- `def create_membrane_query_function()`
- `def membrane_query()`
- `def _find_test_path()`
- `def _path_to_module()`
- `def verify_completion()`
- `def format_verification_feedback()`
- `def all_passed()`
- `def get_failed_membrane_protocols()`
- `def format_escalation_feedback()`
- `def format_todo_suggestion()`
- `def should_suggest_todos()`

**Docs:** `docs/connectome/PATTERNS_Connectome.m`

**Docs:** `docs/membrane/IMPLEMENTATION_Membrane_System.md`

**Definitions:**
- `class StepDefinition`
- `def from_dict()`
- `class ConnectomeDefinition`
- `def from_dict()`
- `def get_step()`
- `def get_start_step()`
- `class ConnectomeLoader`
- `def __init__()`
- `def load()`
- `def load_all()`
- `def load_connectome()`
- `def load_connectome_from_string()`

**Docs:** `docs/membrane/IMPLEMENTATION_Membrane_System.md`

**Definitions:**
- `class PersistenceResult`
- `def format()`
- `class GraphPersistence`
- `def __init__()`
- `def get_existing_node_ids()`
- `def refresh_cache()`
- `def validate_only()`
- `def persist_cluster()`
- `def _persist_node()`
- `def _persist_link()`
- `def node_exists()`
- `def query_nodes()`

**Docs:** `docs/membrane/IMPLEMENTATION_Membrane_System.md`

**Definitions:**
- `class ConnectomeRunner`
- `def __init__()`
- `def register_connectome()`
- `def register_connectome_yaml()`
- `def start()`
- `def continue_session()`
- `def abort()`
- `def get_session()`
- `def _process_current_step()`
- `def _start_sub_protocol()`
- `def _return_from_call()`
- `def _build_response()`
- `def run_connectome()`

**Docs:** `docs/membrane/IMPLEMENTATION_Membrane_System.md`

**Definitions:**
- `class SchemaError`
- `def __init__()`
- `def format()`
- `class ConnectivityError`
- `def __init__()`
- `def format()`
- `def _validate_field()`
- `def validate_node()`
- `def validate_link()`
- `def validate_connectivity()`
- `def validate_cluster()`

**Docs:** `docs/membrane/IMPLEMENTATION_Membrane_System.md`

**Definitions:**
- `class SessionStatus`
- `class LoopState`
- `def current_item()`
- `def is_complete()`
- `def advance()`
- `class CallFrame`
- `class SessionState`
- `def create()`
- `def set_answer()`
- `def get_answer()`
- `def set_context()`
- `def get_context()`
- `def add_created_node()`
- `def add_created_link()`
- `def complete()`
- `def abort()`
- `def set_error()`
- `def push_call()`
- `def pop_call()`
- `def call_depth()`
- `def to_dict()`
- `def register_session()`
- `def unregister_session()`
- `def get_active_sessions()`
- `def get_session()`

**Docs:** `docs/membrane/IMPLEMENTATION_Membrane_System.md`

**Definitions:**
- `class StepResult`
- `class StepProcessor`
- `def __init__()`
- `def process_step()`
- `def _process_ask()`
- `def _process_query()`
- `def _process_create()`
- `def _is_valid_node_id()`
- `def _is_valid_link()`
- `def _expand_node()`
- `def _expand_link()`
- `def _process_update()`
- `def _process_branch()`
- `def _process_call_procedure()`
- `def _process_complete()`
- `def _create_node()`
- `def _create_link()`
- `def _get_preset_query()`
- `def _normalize_query_results()`
- `def _evaluate_condition()`

**Definitions:**
- `def slugify()`
- `def truncate()`
- `def count_items()`
- `def format_list()`
- `def first_item()`
- `def format_value()`
- `def expand_template()`
- `def replace_match()`
- `def resolve_reference()`
- `def get_nested()`
- `def expand_dict()`

**Definitions:**
- `class ValidationError`
- `def __init__()`
- `def validate_input()`
- `def validate_string()`
- `def validate_enum()`
- `def validate_number()`
- `def validate_boolean()`
- `def validate_id()`
- `def validate_id_list()`
- `def validate_string_list()`
- `def coerce_value()`

**Docs:** `docs/infrastructure/database-adapter/PATTERNS_DatabaseAdapter.md`

**Definitions:**
- `class DatabaseAdapter`
- `def graph_name()`
- `def query()`
- `def execute()`
- `def transaction()`
- `def create_index()`
- `def health_check()`
- `def close()`
- `class TransactionAdapter`
- `def query()`
- `def execute()`
- `class DatabaseError`
- `class ConnectionError`
- `class QueryError`

**Docs:** `docs/infrastructure/database-adapter/PATTERNS_DatabaseAdapter.md`

**Definitions:**
- `def load_database_config()`
- `def get_database_adapter()`
- `def clear_adapter_cache()`

**Docs:** `docs/infrastructure/database-adapter/ALGORITHM_DatabaseAdapter.md`

**Definitions:**
- `class FalkorDBAdapter`
- `def __init__()`
- `def _connect()`
- `def graph_name()`
- `def graph()`
- `def query()`
- `def execute()`
- `def transaction()`
- `def create_index()`
- `def health_check()`
- `def close()`
- `def _is_connection_error()`
- `class FalkorDBTransaction`
- `def __init__()`
- `def query()`
- `def execute()`
- `def _commit()`

**Docs:** `docs/infrastructure/database-adapter/ALGORITHM_DatabaseAdapter.md`

**Definitions:**
- `class Neo4jAdapter`
- `def __init__()`
- `def _connect()`
- `def graph_name()`
- `def query()`
- `def execute()`
- `def transaction()`
- `def create_index()`
- `def health_check()`
- `def close()`
- `class Neo4jTransaction`
- `def __init__()`
- `def query()`
- `def execute()`

**Definitions:**
- `def _get_link_embedding()`
- `class LinkCreationMixin`
- `def add_said()`
- `def add_moment_at()`
- `def add_moment_then()`
- `def add_narrative_from_moment()`
- `def add_can_speak()`
- `def add_attached_to()`
- `def add_can_lead_to()`
- `def add_belief()`
- `def add_presence()`
- `def move_character()`
- `def add_possession()`
- `def add_narrative_link()`
- `def add_thing_location()`
- `def add_geography()`
- `def add_contains()`
- `def add_about()`

**Definitions:**
- `class GraphOps`
- `def __init__()`
- `def _query()`
- `def _cosine_similarity()`
- `def _find_similar_nodes()`
- `def check_duplicate()`
- `def add_character()`
- `def add_place()`
- `def add_thing()`
- `def add_narrative()`
- `def add_moment()`
- `def apply_mutations()`
- `def get_graph()`

**Definitions:**
- `class QueryError`
- `def __init__()`
- `class GraphQueries`
- `def __init__()`
- `def _inject_energy_for_node()`
- `def _connect()`
- `def _query()`
- `def query()`
- `def _parse_node()`
- `def get_character()`
- `def get_all_characters()`
- `def get_characters_at()`
- `def get_place()`
- `def get_path_between()`
- `def get_narrative()`
- `def get_character_beliefs()`
- `def get_narrative_believers()`
- `def get_narratives_by_type()`
- `def get_narratives_about()`
- `def get_high_weight_narratives()`
- `def get_contradicting_narratives()`
- `def build_scene_context()`
- `def get_player_location()`
- `def get_queries()`

**Docs:** `docs/infrastructure/api/`

**Definitions:**
- `class ActionRequest`
- `class SceneResponse`
- `class DialogueChunk`
- `class NewPlaythroughRequest`
- `class QueryRequest`
- `def create_app()`
- `def _mutation_event_handler()`
- `def get_orchestrator()`
- `def get_graph_queries()`
- `def get_playthrough_queries()`
- `def get_moment_queries()`
- `def get_graph_ops()`
- `async def health_check()`
- `async def create_playthrough()`
- `async def player_action()`
- `async def get_playthrough()`
- `class MomentClickRequest`
- `class MomentClickResponse`
- `async def moment_click()`
- `async def get_moment_view()`
- `async def get_current_view()`
- `async def get_moment_view_as_scene_tree()`
- `async def update_moment_weight()`
- `async def debug_stream()`
- `async def event_generator()`
- `async def get_map()`
- `async def get_ledger()`
- `async def get_faces()`
- `async def get_chronicle()`
- `async def semantic_query_post()`
- `async def semantic_query_get()`
- `async def inject_event()`

**Definitions:**
- `class CreateGraphRequest`
- `class CreateGraphResponse`
- `class GraphInfo`
- `class QueryRequest`
- `def create_graphs_router()`
- `def get_db()`
- `def clone_graph()`
- `async def create_graph()`
- `async def delete_graph()`
- `async def list_graphs()`
- `async def get_graph_info()`
- `async def list_nodes()`
- `async def query_graph()`
- `async def mutate_graph()`

**Definitions:**
- `def _resolve_graph_name()`
- `def _get_queries()`
- `def _get_traversal()`
- `def _get_surface()`
- `def _get_graph_queries()`
- `class MomentResponse`
- `class TransitionResponse`
- `class CurrentMomentsResponse`
- `class ClickRequest`
- `class ClickResponse`
- `class SurfaceRequest`
- `def create_moments_router()`
- `async def get_current_moments()`
- `async def click_word()`
- `async def get_moment_stats()`
- `async def surface_moment()`
- `async def moment_stream()`
- `async def event_generator()`
- `async def get_moment()`
- `def get_moments_router()`

**Docs:** `docs/infrastructure/api/PATTERNS_Api.md`

**Definitions:**
- `class PlaythroughCreateRequest`
- `class MomentRequest`
- `def _opening_to_scene_tree()`
- `def build_beat_narration()`
- `def _count_branches()`
- `def count_clickables()`
- `def _delete_branch()`
- `def create_playthroughs_router()`
- `def _get_playthrough_queries()`
- `async def create_playthrough()`
- `async def create_scenario_playthrough()`
- `async def send_moment()`
- `def dummy_embed()`
- `async def get_discussion_topics()`
- `async def get_discussion_topic()`
- `async def use_discussion_branch()`

**Docs:** `docs/infrastructure/api/IMPLEMENTATION_Api.md`

**Definitions:**
- `def get_sse_clients()`
- `def register_sse_client()`
- `def unregister_sse_client()`
- `def broadcast_moment_event()`

**Docs:** `docs/infrastructure/tempo/IMPLEMENTATION_Tempo.md`

**Definitions:**
- `class SetSpeedRequest`
- `class PlayerInputRequest`
- `class TempoStateResponse`
- `class QueueSizeUpdate`
- `def create_tempo_router()`
- `async def set_speed()`
- `async def get_tempo_state()`
- `async def player_input()`
- `async def update_queue_size()`
- `async def start_tempo()`
- `async def stop_tempo()`
- `def _get_or_create_controller()`
- `def get_tempo_controller()`

**Definitions:**
- `class ValidationResult`
- `def __post_init__()`
- `class CanonHolder`
- `def __init__()`
- `def actors_exist()`
- `def actors_available()`
- `def no_contradiction()`
- `def causal_chain_valid()`
- `def validate_for_activation()`
- `def activate_moment()`
- `def reject_moment()`
- `def interrupt_moment()`
- `def override_moment()`
- `def recall_moment()`
- `def get_recallable_moments()`
- `def reactivate_moment()`
- `def record_to_canon()`

**Docs:** `docs/infrastructure/database-adapter/PATTERNS_DatabaseAdapter.md`

**Definitions:**
- `class DatabaseAdapter`
- `def graph_name()`
- `def query()`
- `def execute()`
- `def transaction()`
- `def create_index()`
- `def health_check()`
- `def close()`
- `class TransactionAdapter`
- `def query()`
- `def execute()`
- `class DatabaseError`
- `class ConnectionError`
- `class QueryError`

**Docs:** `docs/infrastructure/database-adapter/PATTERNS_DatabaseAdapter.md`

**Definitions:**
- `def _get_repo_name()`
- `def load_database_config()`
- `def get_database_adapter()`
- `def clear_adapter_cache()`

**Docs:** `docs/infrastructure/database-adapter/ALGORITHM_DatabaseAdapter.md`

**Definitions:**
- `class FalkorDBAdapter`
- `def __init__()`
- `def _connect()`
- `def graph_name()`
- `def graph()`
- `def query()`
- `def execute()`
- `def transaction()`
- `def create_index()`
- `def health_check()`
- `def close()`
- `def _is_connection_error()`
- `class FalkorDBTransaction`
- `def __init__()`
- `def query()`
- `def execute()`
- `def _commit()`

**Docs:** `docs/infrastructure/database-adapter/ALGORITHM_DatabaseAdapter.md`

**Definitions:**
- `class Neo4jAdapter`
- `def __init__()`
- `def _connect()`
- `def graph_name()`
- `def query()`
- `def execute()`
- `def transaction()`
- `def create_index()`
- `def health_check()`
- `def close()`
- `class Neo4jTransaction`
- `def __init__()`
- `def query()`
- `def execute()`

**Docs:** `docs/infrastructure/embeddings/`

**Definitions:**
- `def get_embedding()`
- `def cosine_similarity()`

**Definitions:**
- `def embed_all_pending()`
- `def _node_embed_text()`
- `def _link_embed_text()`

**Docs:** `docs/infrastructure/embeddings/`

**Definitions:**
- `class EmbeddingProvider`
- `def embed()`
- `def embed_batch()`
- `def embed_node()`
- `def similarity()`
- `class EmbeddingConfigError`
- `def _check_dimension_mismatch()`
- `def get_embedding_service()`
- `def clear_cache()`

**Docs:** `docs/infrastructure/embeddings/`

**Definitions:**
- `class OpenAIEmbeddingAdapter`
- `def __init__()`
- `def _get_client()`
- `def embed()`
- `def embed_batch()`
- `def embed_node()`
- `def similarity()`

**Docs:** `docs/infrastructure/embeddings/`

**Definitions:**
- `class EmbeddingService`
- `def __init__()`
- `def _load_model()`
- `def embed()`
- `def embed_batch()`
- `def embed_node()`
- `def _node_to_text()`
- `def embed_link()`
- `def similarity()`
- `def get_embedding_service()`

**Docs:** `docs/infrastructure/scene-memory/`

**Definitions:**
- `class MomentProcessor`
- `def __init__()`
- `def _load_transcript_line_count()`
- `def _write_transcript()`
- `def _append_to_transcript()`
- `def set_context()`
- `def process_dialogue()`
- `def process_narration()`
- `def process_player_action()`
- `def process_hint()`
- `def create_possible_moment()`
- `def link_moments()`
- `def link_narrative_to_moments()`
- `def _generate_id()`
- `def _tick_to_time_of_day()`
- `def last_moment_id()`
- `def transcript_line_count()`
- `def get_moment_processor()`

**Definitions:**
- `class AgentCliResult`
- `def get_agent_model()`
- `def _load_dotenv_if_needed()`
- `def build_agent_command()`
- `def run_agent()`
- `def parse_claude_json_output()`
- `def extract_claude_text()`
- `def _strip_code_fence()`
- `def parse_codex_stream_output()`

**Docs:** `docs/agents/narrator/`

**Definitions:**
- `class NarratorService`
- `def __init__()`
- `def generate()`
- `def _build_prompt()`
- `def _call_claude()`
- `def _fallback_response()`
- `def reset_session()`

**Definitions:**
- `class Orchestrator`
- `def __init__()`
- `def process_action()`
- `def process_action_streaming()`
- `def _build_scene_context()`
- `def _get_player_location()`
- `def _get_time_of_day()`
- `def _get_game_day()`
- `def _get_player_goal()`
- `def _get_recent_action()`
- `def _apply_mutations()`
- `def _parse_time()`
- `def _process_flips()`
- `def _build_graph_context()`
- `def _get_character_location_by_id()`
- `def _apply_wr_mutations()`
- `def new_game()`
- `def _world_injection_path()`
- `def _get_world_tick()`
- `def _load_world_injection()`
- `def _save_world_injection()`
- `def _clear_world_injection()`

**Docs:** `docs/agents/world-runner/PATTERNS_World_Runner.md`

**Definitions:**
- `class WorldRunnerService`
- `def __init__()`
- `def process_flips()`
- `def _build_prompt()`
- `def _call_claude()`
- `def _fallback_response()`
- `def run_until_visible()`
- `def run_until_disrupted()`

**Definitions:**
- `class TempoState`
- `class TempoController`
- `def __init__()`
- `def speed()`
- `def running()`
- `def paused()`
- `def tick_count()`
- `def set_speed()`
- `def pause()`
- `def resume()`
- `def _tick_interval()`
- `async def run()`
- `def stop()`

**Docs:** `.mind/docs/AGENT_TEMPLATE.md`

**Definitions:**
- `def ingest_actors()`
- `def _ingest_actor()`

**Docs:** `docs/capabilities/PATTERNS_Capabilities.md`

**Definitions:**
- `def ingest_capabilities()`
- `def _ingest_capability()`
- `def _generate_synthesis()`
- `def _parse_procedure_yaml()`
- `def _extract_procedure_reference()`
- `def _extract_task_references()`

**Definitions:**
- `def _load_required_sections()`
- `def _validate_doc_template()`
- `def _find_modules()`
- `def _escape_content()`
- `def _get_synthesis()`
- `def _parse_impl_references()`
- `def _parse_doc_references()`
- `def ingest_docs_to_graph()`
- `def ensure_space()`
- `def create_task()`
- `def create_doc_node()`
- `def create_impl_links()`
- `def create_doc_reference_links()`
- `def ingest_mind_to_graph()`
- `def ensure_space()`
- `def get_subtype()`
- `def ingest_file()`

**Docs:** `docs/ingest/PATTERNS_File_Ingestion.md`

**Definitions:**
- `def _parse_code_imports()`
- `def scan_and_ingest_files()`
- `def _ensure_space()`
- `def _create_thing()`
- `def _compute_physics_properties()`
- `def _generate_synthesis()`
- `def _scan_dir()`
- `def _embed_all_nodes()`

**Definitions:**
- `class MembraneBroadcast`
- `def __init__()`
- `def _query()`
- `def broadcast_node()`
- `def remove_node()`
- `def sync_all_public()`
- `def get_broadcast()`
- `def on_node_public()`
- `def on_node_private()`

**Definitions:**
- `def _cosine_similarity()`
- `class MembraneQueries`
- `def __init__()`
- `def _query()`
- `def search()`
- `def health_check()`
- `def get_membrane_queries()`

**Definitions:**
- `class StimulusHandler`
- `def __init__()`
- `def handle_query()`
- `def cosine_sim()`
- `def get_stimulus_handler()`

**Docs:** `docs/schema/PATTERNS_Schema.md`

**Definitions:**
- `class ActorType`
- `class Face`
- `class SkillLevel`
- `class VoiceTone`
- `class VoiceStyle`
- `class Approach`
- `class Value`
- `class Flaw`
- `class SpaceType`
- `class Weather`
- `class Mood`
- `class ThingType`
- `class Significance`
- `class NarrativeType`
- `class NarrativeTone`
- `class NarrativeVoiceStyle`
- `class BeliefSource`
- `class PathDifficulty`
- `class MomentType`
- `class MomentStatus`
- `class MomentTrigger`
- `class ModifierType`
- `class ModifierSeverity`
- `class Modifier`
- `class Skills`
- `class ActorVoice`
- `class Personality`
- `class Backstory`
- `class Atmosphere`
- `class NarrativeAbout`
- `class NarrativeVoice`
- `class TimeOfDay`
- `class NarrativeSource`
- `class GameTimestamp`
- `def __str__()`
- `def parse()`
- `def __lt__()`
- `def __le__()`
- `def __gt__()`
- `def __ge__()`

**Definitions:**
- `def _now_s()`
- `class LinkBase`
- `def heat_score()`
- `def is_hot()`
- `def embeddable_text()`
- `def compute_embedding()`
- `def touch()`
- `def mark_traversed()`
- `def blend_emotion_axis()`
- `class ActorNarrative`
- `class NarrativeNarrative`
- `class ActorSpace`
- `class ActorThing`
- `class ThingSpace`
- `class SpaceSpace`
- `def travel_days()`

**Definitions:**
- `def _now_s()`
- `class Actor`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `class Space`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `class Thing`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `class Narrative`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `def is_core_type()`
- `class Moment`
- `def embeddable_text()`
- `def should_embed()`
- `def is_active()`
- `def is_completed()`
- `def is_resolved()`
- `def can_draw_energy()`
- `def radiation_rate()`
- `def touch()`
- `def mark_traversed()`
- `def activate()`
- `def resolve()`

**Docs:** `docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.1_Energy_Physics.md`

**Definitions:**
- `class TickResult`
- `class TickResultV1_1`
- `class GraphTick`
- `def __init__()`
- `def run()`
- `def run_v1_1()`
- `def _phase_generation()`
- `def _phase_moment_draw()`
- `def _phase_moment_flow()`
- `def _phase_narrative_backflow()`
- `def _phase_decay()`
- `def _phase_completion()`
- `def _liquidate_moment()`
- `def _crystallize_actor_links()`
- `def _get_active_moments()`
- `def _count_actors()`
- `def _calculate_total_energy()`
- `def _process_moment_tick()`
- `def _compute_character_energies()`
- `def _compute_relationship_intensity()`
- `def _compute_proximity()`
- `def _get_character_location()`
- `def _parse_distance()`
- `def _flow_energy_to_narratives()`
- `def _propagate_energy()`
- `def _get_narrative_links()`
- `def _decay_energy()`
- `def _update_narrative_weights()`

**Definitions:**
- `class GraphOps`
- `def __init__()`
- `def _query()`
- `def _cosine_similarity()`
- `def _find_similar_nodes()`
- `def check_duplicate()`
- `def add_character()`
- `def add_place()`
- `def add_thing()`
- `def add_narrative()`
- `def add_moment()`
- `def apply_mutations()`
- `def get_graph()`

**Definitions:**
- `class ApplyOperationsMixin`
- `def _generate_node_embedding()`
- `def _get_node_name()`
- `def _generate_link_embedding()`
- `def _set_link_embedding()`
- `def apply()`
- `def _get_existing_node_ids()`
- `def _node_has_links()`
- `def _validate_link_targets()`
- `def _link_id()`
- `def _extract_character_args()`
- `def _extract_place_args()`
- `def _extract_thing_args()`
- `def _extract_narrative_args()`
- `def _extract_moment_args()`
- `def _extract_belief_args()`
- `def _extract_presence_args()`
- `def _extract_possession_args()`
- `def _extract_geography_args()`
- `def _extract_narrative_link_args()`
- `def _extract_thing_location_args()`
- `def _apply_node_update()`

**Definitions:**
- `def _get_link_embedding()`
- `class LinkCreationMixin`
- `def add_said()`
- `def add_moment_at()`
- `def add_moment_then()`
- `def add_narrative_from_moment()`
- `def add_can_speak()`
- `def add_attached_to()`
- `def add_can_lead_to()`
- `def add_belief()`
- `def add_presence()`
- `def move_character()`
- `def add_possession()`
- `def add_narrative_link()`
- `def add_thing_location()`
- `def add_geography()`
- `def add_contains()`
- `def add_about()`

**Definitions:**
- `class MomentOperationsMixin`
- `def handle_click()`
- `def update_moment_weight()`
- `def propagate_embedding_energy()`
- `def _get_current_tick()`
- `def decay_moments()`
- `def on_player_leaves_location()`
- `def on_player_arrives_location()`
- `def garbage_collect_moments()`
- `def boost_moment_weight()`

**Docs:** `docs/physics/graph/PATTERNS_Graph.md`

**Definitions:**
- `class GraphReadOps`
- `def __init__()`
- `def _query()`
- `def _parse_natural_language()`
- `def _collect_nodes_and_links()`
- `def query_cypher()`
- `def list_graphs()`
- `def query_natural_language()`
- `def search_semantic()`
- `def fetch_full_graph()`
- `def get_graph_reader()`

**Definitions:**
- `class QueryError`
- `def __init__()`
- `class GraphQueries`
- `def __init__()`
- `def _inject_energy_for_node()`
- `def _connect()`
- `def _query()`
- `def query()`
- `def _parse_node()`
- `def get_character()`
- `def get_all_characters()`
- `def get_characters_at()`
- `def get_place()`
- `def get_path_between()`
- `def get_narrative()`
- `def get_character_beliefs()`
- `def get_narrative_believers()`
- `def get_narratives_by_type()`
- `def get_narratives_about()`
- `def get_high_weight_narratives()`
- `def get_contradicting_narratives()`
- `def build_scene_context()`
- `def get_player_location()`
- `def get_queries()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `class MomentQueryMixin`
- `def _maybe_inject_energy()`
- `def get_moment()`
- `def get_moments_at_place()`
- `def get_moments_by_character()`
- `def get_moments_in_tick_range()`
- `def get_moment_sequence()`
- `def get_narrative_moments()`
- `def get_narratives_from_moment()`
- `def search_moments()`
- `def _find_similar_moments_by_embedding()`
- `def get_current_view()`
- `def get_live_moments()`
- `def resolve_speaker()`
- `def get_available_transitions()`
- `def get_clickable_words()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `class SearchQueryMixin`
- `def search()`
- `def _create_query_moment()`
- `def _create_semantic_bridges()`
- `def _find_similar_nodes()`
- `def _create_bridge_link()`
- `def _link_actor_to_moment()`
- `def _link_moment_about()`
- `def _tick_local()`
- `def _tick_local_simple()`
- `def _emotional_similarity()`
- `def _update_energy()`
- `def _drain_energy()`
- `def _get_activated_moments()`
- `def _expand_cluster()`
- `def _to_markdown()`
- `def _cosine_similarity()`

**Docs:** `None yet (extracted during monolith split)`

**Definitions:**
- `def cosine_similarity()`
- `def extract_node_props()`
- `def extract_link_props()`
- `def to_markdown()`
- `def calculate_link_resistance()`
- `def dijkstra_with_resistance()`
- `def dijkstra_single_source()`
- `def view_to_scene_tree()`

**Definitions:**
- `class CleanupReport`
- `def cleanup_invalid_nodes()`
- `def fix_node_types_from_labels()`
- `def get_schema_health()`

**Docs:** `docs/physics/HEALTH_Energy_Physics.md`

**Docs:** `docs/physics/HEALTH_Energy_Physics.md#indicator-energy_balance`

**Definitions:**
- `class EnergyConservationChecker`
- `def check()`
- `def _get_total_node_energy()`
- `def _get_total_link_energy()`
- `def _get_counts()`
- `def _calculate_expected_max()`

**Docs:** `docs/physics/HEALTH_Energy_Physics.md#indicator-link_hot_cold_ratio`

**Definitions:**
- `class LinkStateChecker`
- `def check()`
- `def _count_hot_cold_links()`

**Docs:** `docs/physics/HEALTH_Energy_Physics.md#indicator-moment_state_validity`

**Definitions:**
- `class MomentLifecycleChecker`
- `def __init__()`
- `def record_transition()`
- `def clear_transitions()`
- `def check()`
- `def _is_valid_transition()`
- `def _find_invalid_states()`

**Docs:** `docs/physics/HEALTH_Energy_Physics.md#indicator-no_negative_energy`

**Definitions:**
- `class NoNegativeEnergyChecker`
- `def check()`
- `def _find_negative_node_energies()`
- `def _find_negative_link_energies()`

**Definitions:**
- `class SubEntityTreeChecker`
- `def __init__()`
- `def check()`
- `class FoundNarrativesChecker`
- `def __init__()`
- `def check()`
- `class CrystallizationEmbeddingChecker`
- `def __init__()`
- `def check()`
- `class CrystallizedConsistencyChecker`
- `def __init__()`
- `def check()`
- `class SiblingDivergenceChecker`
- `def __init__()`
- `def check()`
- `class LinkScoreChecker`
- `def __init__()`
- `def check()`
- `class CrystallizationNoveltyChecker`
- `def __init__()`
- `def check()`
- `def validate_subentity()`
- `def is_subentity_healthy()`

**Docs:** `docs/physics/HEALTH_Energy_Physics.md#indicator-tick_phase_order`

**Definitions:**
- `class TickIntegrityChecker`
- `def __init__()`
- `def record_phase()`
- `def clear_phases()`
- `def check()`
- `def _verify_order()`
- `def _verify_timestamps()`

**Docs:** `docs/physics/HEALTH_Energy_Physics.md`

**Definitions:**
- `class HealthStatus`
- `class HealthResult`
- `def to_dict()`
- `class BaseChecker`
- `def __init__()`
- `def check()`
- `def ok()`
- `def warn()`
- `def error()`
- `def unknown()`

**Definitions:**
- `class AggregateResult`
- `def to_dict()`
- `def get_graph_connection()`
- `def run_check()`
- `def run_all_checks()`
- `def print_result()`
- `def print_aggregate()`
- `def main()`

**Definitions:**
- `class FailurePattern`
- `def detect_failure_patterns()`
- `def extract_exploration_context()`
- `def extract_termination_info()`
- `def extract_events_summary()`
- `def find_evidence_lines()`
- `def generate_diagnostic_report()`
- `def save_diagnostic_report()`
- `def main()`

**Definitions:**
- `class ExplorationHealthReport`
- `def to_dict()`
- `class StepRecord`
- `def parse_log_file()`
- `class EfficiencyChecker`
- `def __init__()`
- `def check()`
- `class SatisfactionVelocityChecker`
- `def __init__()`
- `def check()`
- `class SiblingDivergenceChecker`
- `def __init__()`
- `def check()`
- `class SemanticQualityChecker`
- `def __init__()`
- `def check()`
- `class BacktrackRateChecker`
- `def __init__()`
- `def check()`
- `class CrystallizationNoveltyChecker`
- `def __init__()`
- `def check()`
- `class AnomalyCountChecker`
- `def __init__()`
- `def check()`
- `def run_exploration_health_checks()`
- `def find_recent_explorations()`
- `def print_health_report()`
- `def parse_duration()`
- `def main()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def phase_completion()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def phase_generation()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def phase_link_cooling()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def _get_link_axes()`
- `def phase_moment_draw()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def _get_link_axes()`
- `def phase_moment_flow()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def phase_moment_interaction()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def _get_link_axes()`
- `def phase_narrative_backflow()`

**Docs:** `docs/physics/IMPLEMENTATION_Physics.md`

**Definitions:**
- `def phase_rejection()`

**Definitions:**
- `class IntentionType`
- `class ClusterNode`
- `class ClusterLink`
- `class RawCluster`
- `class ClusterStats`
- `class Gap`
- `class PresentedCluster`
- `class Marker`
- `def find_direct_response()`
- `def find_convergences()`
- `def find_tensions()`
- `def find_divergences()`
- `def find_gaps()`
- `def build_main_path()`
- `def link_score()`
- `def get_path_node_ids()`
- `def score_node()`
- `def select_nodes()`
- `def filter_links()`
- `def unfold_node_synthesis()`
- `def unfold_link_synthesis()`
- `def format_header()`
- `def format_response()`
- `def format_content_block()`
- `def format_path_tree()`
- `def format_branching()`
- `def format_paths_section()`
- `def format_tension()`
- `def format_tensions_section()`
- `def format_convergences_section()`
- `def format_gaps_section()`
- `def format_stats()`
- `def should_include_section()`
- `def present_cluster()`
- `def cluster_from_dicts()`
- `async def render_cluster()`

**Definitions:**
- `def weighted_embedding_sum()`
- `def mean_embedding()`
- `def compute_crystallization_embedding()`
- `def update_crystallization_embedding_incremental()`
- `def check_novelty()`
- `def find_similar_narratives()`
- `class CrystallizedNarrative`
- `def generate_narrative_id()`
- `def crystallize()`
- `class CrystallizationLink`
- `def generate_crystallization_links()`
- `class SubEntityCrystallizationState`
- `def add_found_narrative()`
- `def add_path_link()`
- `def update_position()`
- `def _update_crystallization()`
- `def get_found_narrative_tuples()`
- `def attempt_crystallization()`

**Docs:** `docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`

**Definitions:**
- `def blend_plutchik_axes()`
- `def target_weight_factor()`
- `def energy_flows_through()`
- `def get_hot_links()`
- `def calculate_flow()`
- `def calculate_received()`
- `def cool_link()`
- `def get_weighted_average_axes()`
- `def blend_embeddings()`
- `def calculate_color_weight()`
- `def forward_color_link()`
- `def compute_link_flow()`
- `def apply_link_traversal()`
- `def inject_node_energy()`
- `def add_node_weight_on_resonating()`
- `def backward_color_path()`
- `def color_link_from_node()`
- `def accumulate_path_energy()`
- `def compute_query_axes()`
- `def compute_path_axes()`
- `def blend_query_axes()`
- `def check_synthesis_drift()`
- `def generate_link_synthesis()`
- `def regenerate_link_synthesis_if_drifted()`
- `def generate_node_synthesis()`
- `def regenerate_node_synthesis_if_drifted()`

**Definitions:**
- `class GraphInterface`
- `class ExplorationResult`
- `def collect_result()`
- `class ExplorationConfig`
- `class ExplorationTimeoutError`
- `class ExplorationRunner`
- `def __init__()`
- `def _log_step()`
- `async def explore()`
- `async def _run_subentity()`
- `async def _step_seeking()`
- `async def _step_branching()`
- `async def _step_absorbing()`
- `async def _step_resonating()`
- `async def _step_reflecting()`
- `async def _step_crystallizing()`
- `async def _step_merging()`
- `async def _update_crystallization_embedding()`
- `async def run_exploration()`
- `def run_exploration_sync()`
- `def present_exploration_result()`

**Docs:** `docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`

**Definitions:**
- `def blend_plutchik_axes()`
- `def target_weight_factor()`
- `def energy_flows_through()`
- `def get_hot_links()`
- `def calculate_flow()`
- `def calculate_received()`
- `def cool_link()`
- `def get_weighted_average_axes()`
- `def blend_embeddings()`
- `def calculate_color_weight()`
- `def forward_color_link()`
- `def compute_link_flow()`
- `def apply_link_traversal()`
- `def inject_node_energy()`
- `def add_node_weight_on_resonating()`
- `def backward_color_path()`
- `def color_link_from_node()`
- `def accumulate_path_energy()`
- `def compute_query_axes()`
- `def compute_path_axes()`
- `def blend_query_axes()`
- `def check_synthesis_drift()`
- `def generate_link_synthesis()`
- `def regenerate_link_synthesis_if_drifted()`
- `def generate_node_synthesis()`
- `def regenerate_node_synthesis_if_drifted()`

**Definitions:**
- `def _load_nature()`
- `def _get_all_verbs()`
- `def get_defaults()`
- `def get_pre_modifiers()`
- `def get_post_modifiers()`
- `def get_weight_annotations()`
- `def get_intensifiers()`
- `def get_translations()`
- `def get_synonyms()`
- `def _build_reverse_synonyms()`
- `def resolve_synonym()`
- `def _resolve_nature_string()`
- `def parse_nature()`
- `def nature_to_floats()`
- `def parse_with_conflicts()`
- `def apply_values()`
- `def get_intensified_verb()`
- `def select_verb_form()`
- `def translate()`
- `def get_verb_for_nature()`
- `def get_nature_reference()`
- `def get_nature_compact()`
- `def reload_nature()`

**Definitions:**
- `class ExplorationContext`
- `def __init__()`
- `def register()`
- `def get()`
- `def exists()`
- `def unregister()`
- `def all_active()`
- `class SubEntityState`
- `class SubEntityTransitionError`
- `class SubEntity`
- `def __post_init__()`
- `def intention_weight()`
- `def parent()`
- `def siblings()`
- `def children()`
- `def can_transition_to()`
- `def transition_to()`
- `def is_terminal()`
- `def is_active()`
- `def run_node()`
- `def focus_node()`
- `def criticality()`
- `def compute_energy_injection()`
- `def inject_energy_to_node()`
- `def inject_energy_to_link()`
- `def update_depth()`
- `def update_progress()`
- `def is_fatigued()`
- `def update_crystallization_embedding()`
- `def run_child()`
- `def set_sibling_references()`
- `def merge_child_results()`
- `def get_emotions()`
- `def blend_emotions()`
- `def blend()`
- `def update_satisfaction()`
- `def to_dict()`
- `def cosine_similarity()`
- `def compute_self_novelty()`
- `def compute_sibling_divergence()`
- `def compute_link_score()`
- `def should_child_crystallize()`
- `def create_subentity()`

**Docs:** `docs/schema/GRAMMAR_Link_Synthesis.md`

**Definitions:**
- `class LinkPhysics`
- `def get_base_verb_key()`
- `def compute_intensity()`
- `def apply_intensifier()`
- `def get_pre_modifiers()`
- `def get_post_modifiers()`
- `def get_weight_annotation()`
- `def synthesize_link()`
- `def synthesize_from_dict()`
- `class ParsedPhysics`
- `def parse_phrase()`
- `def parse_and_merge()`
- `def synthesize_narrative_name()`
- `def synthesize_narrative_content()`
- `def synthesize_from_crystallization()`
- `def _get_energy_state()`
- `def _get_importance()`
- `def synthesize_node()`
- `def synthesize_link_full()`

**Definitions:**
- `class ParsedNodeSynthesis`
- `class ParsedLinkSynthesis`
- `def to_adverb()`
- `def to_participle()`
- `def parse_node_synthesis()`
- `def parse_link_synthesis()`
- `def unfold_node()`
- `def unfold_link()`
- `def unfold_node_link_node()`
- `def compact_node()`
- `def compact_link()`

**Definitions:**
- `class LogLevel`
- `class AnomalySeverity`
- `class LinkCandidate`
- `def to_dict()`
- `class Anomaly`
- `def to_dict()`
- `class CausalLink`
- `def to_dict()`
- `class LearningSignal`
- `def to_dict()`
- `class IntentionConcept`
- `class DecisionInfo`
- `def to_dict()`
- `class MovementInfo`
- `def to_dict()`
- `class ExplorationContext`
- `def to_dict()`
- `class ExplorationStartContext`
- `def to_dict()`
- `class TerminationInfo`
- `def to_dict()`
- `class EnergyInjection`
- `def to_dict()`
- `class StepRecord`
- `def to_dict()`
- `def generate_state_diagram()`
- `class ExplanationGenerator`
- `def explain_link_selection()`
- `def explain_branch()`
- `def explain_dead_end()`
- `def explain_resonance()`
- `def generate_why_not()`
- `class AnomalyDetector`
- `def detect_anomalies()`
- `class CausalChainBuilder`
- `def build_chain()`
- `class LearningSignalExtractor`
- `def extract_signals()`
- `class TraversalLogger`
- `def __init__()`
- `def _timestamp()`
- `def _write_jsonl()`
- `def _write_human()`
- `def exploration_start()`
- `def exploration_end()`
- `def log_step()`
- `def _generate_progress_narrative()`
- `def _build_exploration_context()`
- `def _format_step_human()`
- `def log_branch()`
- `def log_merge()`
- `def log_crystallize()`
- `def log_energy_injection()`
- `def generate_exploration_id()`
- `def get_traversal_logger()`
- `def create_traversal_logger()`

**Definitions:**
- `class ActorType`
- `class Face`
- `class SkillLevel`
- `class VoiceTone`
- `class VoiceStyle`
- `class Approach`
- `class Value`
- `class Flaw`
- `class SpaceType`
- `class Weather`
- `class Mood`
- `class ThingType`
- `class Significance`
- `class NarrativeType`
- `class NarrativeTone`
- `class NarrativeVoiceStyle`
- `class BeliefSource`
- `class PathDifficulty`
- `class MomentType`
- `class MomentStatus`
- `class MomentTrigger`
- `class ModifierType`
- `class ModifierSeverity`
- `class Modifier`
- `class Skills`
- `class ActorVoice`
- `class Personality`
- `class Backstory`
- `class Atmosphere`
- `class NarrativeAbout`
- `class NarrativeVoice`
- `class TimeOfDay`
- `class NarrativeSource`
- `class GameTimestamp`
- `def __str__()`
- `def parse()`
- `def __lt__()`
- `def __le__()`
- `def __gt__()`
- `def __ge__()`

**Definitions:**
- `def _now_s()`
- `class LinkBase`
- `def heat_score()`
- `def is_hot()`
- `def embeddable_text()`
- `def compute_embedding()`
- `def touch()`
- `def mark_traversed()`
- `def blend_emotion_axis()`
- `class ActorNarrative`
- `class NarrativeNarrative`
- `class ActorSpace`
- `class ActorThing`
- `class ThingSpace`
- `class SpaceSpace`
- `def travel_days()`

**Definitions:**
- `def _now_s()`
- `class Actor`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `class Space`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `class Thing`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `class Narrative`
- `def embeddable_text()`
- `def touch()`
- `def mark_traversed()`
- `def is_core_type()`
- `class Moment`
- `def embeddable_text()`
- `def should_embed()`
- `def is_active()`
- `def is_completed()`
- `def is_resolved()`
- `def can_draw_energy()`
- `def radiation_rate()`
- `def touch()`
- `def mark_traversed()`
- `def activate()`
- `def resolve()`

**Docs:** `docs/infrastructure/embeddings/`

**Definitions:**
- `class EmbeddingService`
- `def __init__()`
- `def _load_model()`
- `def embed()`
- `def embed_batch()`
- `def embed_node()`
- `def _node_to_text()`
- `def embed_link()`
- `def similarity()`
- `def get_embedding_service()`

**Definitions:**
- `class MomentOperationsMixin`
- `def handle_click()`
- `def update_moment_weight()`
- `def propagate_embedding_energy()`
- `def _get_current_tick()`
- `def decay_moments()`
- `def on_player_leaves_location()`
- `def on_player_arrives_location()`
- `def garbage_collect_moments()`
- `def boost_moment_weight()`

**Docs:** `docs/mind_cli_core/OBJECTIVES_mind_cli_core.md`

**Definitions:**
- `def _add_module_translation_args()`
- `def _validate_module_translation()`
- `def _add_refactor_conflict_args()`
- `def _validate_refactor_conflicts()`
- `def main()`

**Definitions:**
- `class ConnectionScore`
- `def calculate_verdict()`
- `class LinkSuggestion`
- `class TargetValidation`
- `class ClusterMetrics`
- `def __init__()`
- `def score_cluster()`
- `def format_score()`
- `def validate_targets()`
- `def _get_node_type()`
- `def suggest_links()`
- `def _find_nodes_of_type()`
- `def format_suggestions()`
- `class ClusterValidator`
- `def __init__()`
- `def validate_cluster()`
- `def _build_report()`
- `def score_cluster_command()`
- `def cluster_validate_command()`

**Definitions:**
- `def get_graph_interface()`
- `def _query()`
- `def _parse_embedding()`
- `def _node_to_dict()`
- `def _rel_to_dict()`
- `async def get_node()`
- `async def get_node_embedding()`
- `async def get_outgoing_links()`
- `async def get_incoming_links()`
- `async def get_link()`
- `async def get_link_embedding()`
- `async def get_all_narratives()`
- `async def is_narrative()`
- `async def is_moment()`
- `async def update_link()`
- `async def create_narrative()`
- `async def create_link()`
- `def _get_mock_graph_interface()`
- `async def get_node()`
- `async def get_node_embedding()`
- `async def get_outgoing_links()`
- `async def get_incoming_links()`
- `async def get_link_embedding()`
- `async def get_all_narratives()`
- `async def is_narrative()`
- `async def is_moment()`
- `async def update_link()`
- `async def create_narrative()`
- `async def create_link()`
- `def get_embedding()`
- `def format_result()`
- `async def run_exploration()`
- `def explore_command()`

**Docs:** `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`

**Definitions:**
- `def _get_mind_root()`
- `def _configure_mcp_membrane()`
- `def _generate_mcp_config_file()`
- `def _escape_marker_tokens()`
- `def _copy_skills()`
- `def _update_or_add_section()`
- `def _update_root_claude_md()`
- `def _build_root_claude_section()`
- `def _build_system_prompt()`
- `def _build_claude_addition()`
- `def _build_gemini_addition()`
- `def _build_agents_addition()`
- `def _build_manager_agents_addition()`
- `def _remove_write_permissions()`
- `def _enforce_readonly_for_views()`
- `def _enforce_readonly_for_templates()`
- `def _init_graph()`
- `def init_protocol()`
- `def copy_protocol_partial()`

**Definitions:**
- `def set_actor()`
- `def clear_context()`
- `def get_actor()`
- `def get_context()`
- `def _detect_active_task()`
- `def _throttler_allows_running()`
- `def _resolve_active_space()`
- `def _create_moment()`
- `def _apply_context_links()`
- `def _inject_link_raw()`
- `def normalize_id()`
- `def validate_id()`
- `def parse_id()`
- `def _generate_node_synthesis()`
- `def _generate_link_synthesis()`
- `def _get_embedding_service()`
- `def _generate_embedding()`
- `def _nature_to_physics()`
- `def inject()`
- `def _inject_node()`
- `def _inject_link()`
- `def inject_batch()`
- `def inject_node()`
- `def inject_link()`

**Definitions:**
- `def _get_cluster_validator()`
- `def _get_markdown_sync()`
- `class ProcedureStep`
- `class ProcedureResult`
- `def slugify()`
- `def expand_template()`
- `def replace()`
- `def expand_dict()`
- `class ProtocolRunner`
- `def __init__()`
- `def run()`
- `def _parse_step()`
- `def _parse_step_v2()`
- `def _run_steps_v2()`
- `def _run_step_v2()`
- `def _run_query_step()`
- `def _execute_query_v2()`
- `def _run_branch_step()`
- `def _evaluate_condition_v2()`
- `def _run_ask_step()`
- `def _run_create_step()`
- `def _run_call_procedure_step()`
- `def _run_step()`
- `def _create_node()`
- `def _create_link()`
- `def _create_links_foreach()`
- `def _update_node()`
- `def _validate_check()`
- `def _create_completion_moment()`
- `def _find_actor_last_moment()`
- `def _execute_query()`
- `def _upsert_node()`
- `def _upsert_link()`
- `def _node_exists()`
- `def _get_from_context()`
- `def _evaluate_condition()`
- `def _sync_narratives_to_markdown()`
- `def _default_answer_provider()`
- `class StepError`
- `def run_protocol_command()`
- `def preset_answers()`

**Docs:** `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`

**Definitions:**
- `class FileInfo`
- `class DependencyInfo`
- `class RepoOverview`
- `def get_language()`
- `def extract_docs_ref()`
- `def extract_markdown_sections()`
- `def extract_markdown_code_refs()`
- `def extract_markdown_doc_refs()`
- `def extract_code_definitions()`
- `def count_chars()`
- `def _filter_local_imports()`
- `def build_file_tree()`
- `def get_dependency_info()`
- `def count_tree_stats()`
- `def traverse()`
- `def count_docs_structure()`
- `def generate_repo_overview()`
- `def _save_single_map()`
- `def generate_and_save()`

**Docs:** `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture.md`

**Definitions:**
- `class Colors`
- `def colorize()`
- `def maturity_color()`
- `def severity_color()`
- `def doc_status_color()`
- `class DocChainStatus`
- `def completeness_score()`
- `def to_bar()`
- `def get_all_docs()`
- `class HealthIssue`
- `class ModuleStatus`
- `def load_modules_yaml()`
- `def extract_doc_status()`
- `def find_doc_chain()`
- `def extract_sync_details()`
- `def _path_matches_glob()`
- `def get_all_health_issues()`
- `def get_module_health_issues()`
- `def filter_issues_for_module()`
- `def get_module_status()`
- `def get_all_modules_status()`
- `def format_module_status()`
- `def _get_dashboard_data()`
- `def format_dashboard()`
- `def format_global_status()`
- `def status_command()`

**Docs:** `specs/symbol-extraction.yaml`

**Definitions:**
- `class ExtractedSymbol`
- `class ExtractedLink`
- `class ExtractionResult`
- `def slugify()`
- `def calculate_complexity()`
- `def get_docstring_first_line()`
- `def get_return_annotation()`
- `def get_signature()`
- `def has_decorator()`
- `def get_decorators()`
- `class PythonExtractor`
- `def __init__()`
- `def extract_file()`
- `def _extract_imports_raw()`
- `def _extract_function()`
- `def _extract_class()`
- `def _extract_method()`
- `def _extract_constants()`
- `def _extract_annotated_constant()`
- `def _is_literal()`
- `def _extract_calls()`
- `def _extract_import_links()`
- `def _is_external_module()`
- `def _resolve_import()`
- `class TestInferrer`
- `def __init__()`
- `def infer_test_links()`
- `def _create_test_link()`
- `def _extract_explicit_markers()`
- `def _find_test_at_line()`
- `class DocsLinker`
- `def __init__()`
- `def link_docs()`
- `def _find_narrative_docs()`
- `def _extract_docs_markers()`
- `def _find_symbol_references()`
- `def _link_by_module_convention()`
- `class SymbolExtractor`
- `def __init__()`
- `def _connect_graph()`
- `def extract_directory()`
- `def _iter_source_files()`
- `def _upsert_to_graph()`
- `def _upsert_symbol()`
- `def _upsert_link()`
- `def extract_symbols_command()`

**Docs:** `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`

**Definitions:**
- `class ValidationResult`
- `def check_protocol_installed()`
- `def check_project_sync_exists()`
- `def check_module_docs_minimum()`
- `def check_full_chain()`
- `def check_chain_links()`
- `def check_naming_conventions()`
- `def check_views_exist()`
- `def check_module_manifest()`
- `def generate_fix_prompt()`
- `def validate_protocol()`

**Code refs:**
- `doctor_cli_parser_and_run_checker.py`
- `semantic_proximity_based_character_node_selector.py`
- `snake_case.py`

**Sections:**
- # mind-mcp - Agent Instructions
- # Working Principles
- ## Architecture: One Solution Per Problem
- ## Verification: Test Before Claiming Built
- ## Communication: Depth Over Brevity
- ## Quality: Never Degrade
- ## Code Discipline: No Safety Theater
- ## Experience: User Before Infrastructure
- ## Feedback Loop: Human-Agent Collaboration
- ## How These Principles Integrate
- # mind Framework
- ## WHY THIS PROTOCOL EXISTS
- ## COMPANION: PRINCIPLES.md
- ## THE CORE INSIGHT
- ## HOW TO USE THIS
- ## FILE TYPES AND THEIR PURPOSE
- ## KEY PRINCIPLES (from PRINCIPLES.md)
- ## STRUCTURING YOUR DOCS
- ## WHEN DOCS DON'T EXIST
- ## THE DOCUMENTATION PROCESS
- ## Maturity
- ## NAMING ENGINEERING PRINCIPLES
- ## MARKERS
- ## CLI COMMANDS
- # Run scripts with local runtime
- # my_script.py - imports work normally
- ## MCP MEMBRANE TOOLS
- ## MIND UNIVERSAL SCHEMA
- ## THE PROTOCOL IS A TOOL
- ## Before Any Task
- ## After Any Change

**Sections:**
- # mind-mcp
- ## Install
- ## Quick Start
- # Initialize a project
- # Start FalkorDB (default backend)
- ## Agents
- ## ID Convention
- ## MCP Server
- ## CLI
- ## Database Backends
- ## Project Structure
- ## Requirements
- ## License

**Code refs:**
- `Next.js`
- `Node.js`
- `__init__.py`
- `__main__.py`
- `adapter.py`
- `agent_cli.py`
- `agents/handler.py`
- `agents/prompts.py`
- `agents/response.py`
- `app.py`
- `app/api/connectome/tick/route.ts`
- `app/api/sse/route.ts`
- `approval/notifications.py`
- `approval/queue.py`
- `approval/tiers.py`
- `base.py`
- `building/config/mapping.py`
- `building/ingest/create.py`
- `building/ingest/discover.py`
- `building/ingest/parse.py`
- `check_github_for_latest_version.py`
- `check_health.py`
- `check_mind_status_in_directory.py`
- `cli.py`
- `cli/__main__.py`
- `cli/commands/fix_embeddings.py`
- `cli/commands/init.py`
- `cli/commands/status.py`
- `cli/commands/upgrade.py`
- `cli/config.py`
- `cli/helpers/generate_embeddings_for_graph_nodes.py`
- `cli/helpers/ingest_repo_files_to_graph.py`
- `cli/helpers/inject_seed_yaml_to_graph.py`
- `cli/helpers/show_upgrade_notice_if_available.py`
- `cluster_presentation.py`
- `config.py`
- `config/agents.py`
- `config/mapping.py`
- `connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `content/inference.py`
- `content/moment.py`
- `content/narrative.py`
- `context.py`
- `context/format.py`
- `context/query.py`
- `copy_ecosystem_templates_to_target.py`
- `copy_runtime_package_to_target.py`
- `core_utils.py`
- `create_ai_config_files_for_claude_agents_gemini.py`
- `create_database_config_yaml.py`
- `create_env_example_file.py`
- `create_mcp_config_json.py`
- `crystallization.py`
- `deployment/backup.py`
- `deployment/deployer.py`
- `deployment/monitor.py`
- `deployment/rollback.py`
- `diagnosis/evidence.py`
- `diagnosis/layer_attribution.py`
- `diagnosis/pattern_detector.py`
- `diffusion_sim_v2.py`
- `doc_chain.py`
- `doctor.py`
- `doctor_checks.py`
- `doctor_cli_parser_and_run_checker.py`
- `doctor_report.py`
- `engine/connectome/persistence.py`
- `engine/connectome/schema.py`
- `exploration.py`
- `factory.py`
- `falkordb_adapter.py`
- `fix_embeddings_for_nodes_and_links.py`
- `flow.py`
- `frontend/app/scenarios/page.tsx`
- `frontend/app/start/page.tsx`
- `frontend/hooks/useGameState.ts`
- `gemini_agent.py`
- `generate_repo_overview_maps.py`
- `get_mcp_version_from_config.py`
- `get_paths_for_templates_and_runtime.py`
- `graph_interface.py`
- `graph_ops.py`
- `graph_ops_apply.py`
- `graph_ops_events.py`
- `graph_ops_image.py`
- `graph_ops_moments.py`
- `graph_ops_read_only_interface.py`
- `graph_ops_types.py`
- `graph_queries.py`
- `graph_queries_search.py`
- `ingest/__init__.py`
- `ingest/create.py`
- `ingest/discover.py`
- `ingest/markers.py`
- `ingest/parse.py`
- `ingest_repo_files_to_graph.py`
- `inject_seed_yaml_to_graph.py`
- `learning/embeddings.py`
- `learning/extractor.py`
- `learning/pattern_library.py`
- `link_scoring.py`
- `loop.py`
- `mcp/server.py`
- `mind/api/app.py`
- `mind/cli.py`
- `mind/core_utils.py`
- `mind/graph/health/check_health.py`
- `mind/llms/gemini_agent.py`
- `mind/prompt.py`
- `mind/repair.py`
- `mind/repair_verification.py`
- `mind/tests/test_moment.py`
- `mind/validate.py`
- `mock_adapter.py`
- `models.py`
- `moment_processor.py`
- `narrator.py`
- `narrator/prompt_builder.py`
- `nature.py`
- `neo4j_adapter.py`
- `nodes.py`
- `orchestrator.py`
- `persistence.py`
- `phases/completion.py`
- `phases/generation.py`
- `phases/link_cooling.py`
- `phases/moment_draw.py`
- `phases/moment_flow.py`
- `phases/moment_interaction.py`
- `phases/narrative_backflow.py`
- `phases/rejection.py`
- `procedure_runner.py`
- `proposals/generator.py`
- `proposals/scorer.py`
- `proposals/types.py`
- `protocol_runner.py`
- `repair_verification.py`
- `route.ts`
- `runtime/agent_cli.py`
- `runtime/agents/postures.py`
- `runtime/api/app.py`
- `runtime/cli.py`
- `runtime/cluster_builder.py`
- `runtime/cluster_health.py`
- `runtime/cluster_metrics.py`
- `runtime/connectome/persistence.py`
- `runtime/connectome/procedure_runner.py`
- `runtime/connectome/runner.py`
- `runtime/connectome/schema.py`
- `runtime/connectome/session.py`
- `runtime/connectome/steps.py`
- `runtime/connectome/templates.py`
- `runtime/connectome/validation.py`
- `runtime/context.py`
- `runtime/core_utils.py`
- `runtime/doc_extractor.py`
- `runtime/doctor.py`
- `runtime/doctor_checks.py`
- `runtime/doctor_checks_content.py`
- `runtime/doctor_checks_core.py`
- `runtime/doctor_checks_docs.py`
- `runtime/doctor_checks_membrane.py`
- `runtime/doctor_checks_metadata.py`
- `runtime/doctor_checks_naming.py`
- `runtime/doctor_checks_prompt_integrity.py`
- `runtime/doctor_checks_quality.py`
- `runtime/doctor_checks_reference.py`
- `runtime/doctor_checks_stub.py`
- `runtime/doctor_checks_sync.py`
- `runtime/doctor_files.py`
- `runtime/doctor_graph.py`
- `runtime/doctor_report.py`
- `runtime/doctor_types.py`
- `runtime/github.py`
- `runtime/graph/health/check_health.py`
- `runtime/graph/health/lint_terminology.py`
- `runtime/graph/health/test_schema.py`
- `runtime/handlers/base.py`
- `runtime/health/procedure_health.py`
- `runtime/infrastructure/api/app.py`
- `runtime/infrastructure/api/graphs.py`
- `runtime/infrastructure/api/moments.py`
- `runtime/infrastructure/api/playthroughs.py`
- `runtime/infrastructure/api/sse_broadcast.py`
- `runtime/infrastructure/api/tempo.py`
- `runtime/infrastructure/canon/canon_holder.py`
- `runtime/infrastructure/database/__init__.py`
- `runtime/infrastructure/database/adapter.py`
- `runtime/infrastructure/database/factory.py`
- `runtime/infrastructure/database/falkordb_adapter.py`
- `runtime/infrastructure/database/neo4j_adapter.py`
- `runtime/infrastructure/embeddings/service.py`
- `runtime/infrastructure/memory/__init__.py`
- `runtime/infrastructure/memory/moment_processor.py`
- `runtime/infrastructure/memory/transcript.py`
- `runtime/infrastructure/orchestration/agent_cli.py`
- `runtime/infrastructure/orchestration/narrator.py`
- `runtime/infrastructure/orchestration/orchestrator.py`
- `runtime/infrastructure/orchestration/world_runner.py`
- `runtime/infrastructure/tempo/health_check.py`
- `runtime/infrastructure/tempo/tempo_controller.py`
- `runtime/init_cmd.py`
- `runtime/init_db.py`
- `runtime/llms/gemini_agent.py`
- `runtime/llms/tool_helpers.py`
- `runtime/membrane/functions.py`
- `runtime/membrane/health_check.py`
- `runtime/membrane/provider.py`
- `runtime/migrations/migrate_001_schema_alignment.py`
- `runtime/migrations/migrate_temporal_v171.py`
- `runtime/migrations/migrate_tick_to_tick_created.py`
- `runtime/migrations/migrate_to_content_field.py`
- `runtime/migrations/migrate_to_v2_schema.py`
- `runtime/models/__init__.py`
- `runtime/models/base.py`
- `runtime/models/links.py`
- `runtime/models/nodes.py`
- `runtime/moment_graph/__init__.py`
- `runtime/moment_graph/queries.py`
- `runtime/moment_graph/surface.py`
- `runtime/moment_graph/traversal.py`
- `runtime/moments/__init__.py`
- `runtime/physics/__init__.py`
- `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`
- `runtime/physics/cluster_energy_monitor.py`
- `runtime/physics/cluster_presentation.py`
- `runtime/physics/constants.py`
- `runtime/physics/contradiction_pressure_from_negative_polarity_mechanism.py`
- `runtime/physics/crystallization.py`
- `runtime/physics/display_snap_transition_checker.py`
- `runtime/physics/exploration.py`
- `runtime/physics/flow.py`
- `runtime/physics/graph/adapters/__init__.py`
- `runtime/physics/graph/adapters/base.py`
- `runtime/physics/graph/adapters/falkordb_adapter.py`
- `runtime/physics/graph/adapters/mock_adapter.py`
- `runtime/physics/graph/adapters/neo4j_adapter.py`
- `runtime/physics/graph/connectome_read_cli.py`
- `runtime/physics/graph/graph_interface.py`
- `runtime/physics/graph/graph_ops.py`
- `runtime/physics/graph/graph_ops_apply.py`
- `runtime/physics/graph/graph_ops_events.py`
- `runtime/physics/graph/graph_ops_links.py`
- `runtime/physics/graph/graph_ops_moments.py`
- `runtime/physics/graph/graph_ops_read_only_interface.py`
- `runtime/physics/graph/graph_ops_types.py`
- `runtime/physics/graph/graph_queries.py`
- `runtime/physics/graph/graph_queries_moments.py`
- `runtime/physics/graph/graph_queries_search.py`
- `runtime/physics/graph/graph_query_utils.py`
- `runtime/physics/health/check_subentity.py`
- `runtime/physics/health/checker.py`
- `runtime/physics/health/checkers/energy_conservation.py`
- `runtime/physics/health/checkers/moment_lifecycle.py`
- `runtime/physics/link_scoring.py`
- `runtime/physics/nature.py`
- `runtime/physics/phases/completion.py`
- `runtime/physics/phases/generation.py`
- `runtime/physics/phases/link_cooling.py`
- `runtime/physics/phases/moment_draw.py`
- `runtime/physics/phases/moment_flow.py`
- `runtime/physics/phases/moment_interaction.py`
- `runtime/physics/phases/narrative_backflow.py`
- `runtime/physics/phases/rejection.py`
- `runtime/physics/primes_lag_and_half_life_decay_mechanism.py`
- `runtime/physics/subentity.py`
- `runtime/physics/synthesis.py`
- `runtime/physics/synthesis_unfold.py`
- `runtime/physics/tick.py`
- `runtime/physics/tick_v1_2.py`
- `runtime/physics/tick_v1_2_queries.py`
- `runtime/physics/tick_v1_2_types.py`
- `runtime/physics/traversal_logger.py`
- `runtime/project_map.py`
- `runtime/project_map_html.py`
- `runtime/prompt.py`
- `runtime/protocol_runner.py`
- `runtime/protocol_validator.py`
- `runtime/refactor.py`
- `runtime/repair.py`
- `runtime/repair_core.py`
- `runtime/repair_escalation_interactive.py`
- `runtime/repair_instructions.py`
- `runtime/repair_instructions_docs.py`
- `runtime/repair_report.py`
- `runtime/repair_verification.py`
- `runtime/repo_overview.py`
- `runtime/repo_overview_formatters.py`
- `runtime/solve_escalations.py`
- `runtime/symbol_extractor.py`
- `runtime/sync.py`
- `runtime/tests/test_cluster_energy_monitor.py`
- `runtime/tests/test_cluster_presentation.py`
- `runtime/tests/test_e2e_moment_graph.py`
- `runtime/tests/test_energy_v1_2.py`
- `runtime/tests/test_moment.py`
- `runtime/tests/test_moment_graph.py`
- `runtime/tests/test_moment_lifecycle.py`
- `runtime/tests/test_moments_api.py`
- `runtime/tests/test_physics_display_snap.py`
- `runtime/tests/test_router_schema_validation.py`
- `runtime/tests/test_subentity.py`
- `runtime/tests/test_traversal_logger.py`
- `runtime/validate.py`
- `runtime/work.py`
- `scripts/check_chain_links.py`
- `scripts/check_doc_completeness.py`
- `scripts/check_doc_refs.py`
- `scripts/check_orphans.py`
- `semantic_proximity_based_character_node_selector.py`
- `setup_database_and_apply_schema.py`
- `show_upgrade_notice_if_available.py`
- `signals/aggregator.py`
- `signals/collector.py`
- `snake_case.py`
- `stream_dialogue.py`
- `surface.py`
- `sync_skills_to_ai_tool_directories.py`
- `synthesis.py`
- `test_loader.py`
- `test_runner.py`
- `test_schema.py`
- `test_schema_links.py`
- `test_schema_nodes.py`
- `test_session.py`
- `test_steps.py`
- `test_validation.py`
- `tests/building/test_agents.py`
- `tests/building/test_ingest.py`
- `tests/mind/test_cli.py`
- `tests/mind/test_cluster_builder.py`
- `tests/runtime/test_cli.py`
- `tests/runtime/test_cluster_builder.py`
- `tests/test_cluster_stability.py`
- `tick.py`
- `tools/archive/migrate_schema_v11.py`
- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `tools/coverage/validate.py`
- `tools/mcp/membrane_server.py`
- `tools/migrate_v11_fields.py`
- `tools/stream_dialogue.py`
- `tools/test_health_live.py`
- `update_gitignore_with_runtime_entry.py`
- `utils.py`
- `validate_embedding_config_matches_stored.py`
- `validation/modes/shadow.py`
- `validation/modes/unit_test.py`
- `validation/validator.py`

**Doc refs:**
- `agents/narrator/CLAUDE.md`
- `agents/narrator/CLAUDE_old.md`
- `agents/world_runner/CLAUDE.md`
- `algorithms/ALGORITHM_Physics_Energy_Flow_Sources_Sinks_And_Moment_Dynamics.md`
- `algorithms/ALGORITHM_Physics_Energy_Mechanics_And_Link_Semantics.md`
- `algorithms/ALGORITHM_Physics_Handler_And_Input_Processing_Flows.md`
- `algorithms/ALGORITHM_Physics_Mechanisms.md`
- `algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`
- `algorithms/ALGORITHM_Physics_Speed_Control_And_Display_Filtering.md`
- `algorithms/ALGORITHM_Physics_Tick_Cycle_Gating_Flips_And_Dispatch.md`
- `archive/SYNC_CLI_Development_State_archive_2025-12.md`
- `archive/SYNC_archive_2024-12.md`
- `data/ARCHITECTURE — Cybernetic Studio.md`
- `data/MIND Documentation Chain Pattern (Draft “Marco”).md`
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`
- `docs/agents/PATTERNS_Agent_System.md`
- `docs/agents/narrator/ALGORITHM_Scene_Generation.md`
- `docs/agents/narrator/BEHAVIORS_Narrator.md`
- `docs/agents/narrator/HANDOFF_Rolling_Window_Architecture.md`
- `docs/agents/narrator/HEALTH_Narrator.md`
- `docs/agents/narrator/IMPLEMENTATION_Narrator.md`
- `docs/agents/narrator/INPUT_REFERENCE.md`
- `docs/agents/narrator/PATTERNS_Narrator.md`
- `docs/agents/narrator/PATTERNS_World_Building.md`
- `docs/agents/narrator/SYNC_Narrator.md`
- `docs/agents/narrator/SYNC_Narrator_archive_2025-12.md`
- `docs/agents/narrator/TEST_Narrator.md`
- `docs/agents/narrator/TOOL_REFERENCE.md`
- `docs/agents/narrator/VALIDATION_Narrator.md`
- `docs/agents/narrator/archive/SYNC_archive_2024-12.md`
- `docs/architecture/cybernetic_studio_architecture/ALGORITHM_Cybernetic_Studio_Process_Flow.md`
- `docs/architecture/cybernetic_studio_architecture/BEHAVIORS_Cybernetic_Studio_System_Behaviors.md`
- `docs/architecture/cybernetic_studio_architecture/HEALTH_Cybernetic_Studio_Health_Checks.md`
- `docs/architecture/cybernetic_studio_architecture/IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md`
- `docs/architecture/cybernetic_studio_architecture/PATTERNS_Cybernetic_Studio_Architecture.md`
- `docs/architecture/cybernetic_studio_architecture/SYNC_Cybernetic_Studio_Architecture_State.md`
- `docs/architecture/cybernetic_studio_architecture/VALIDATION_Cybernetic_Studio_Architectural_Invariants.md`
- `docs/capabilities/PATTERNS_Capabilities.md`
- `docs/cli/ALGORITHM_CLI_Command_Execution_Logic.md`
- `docs/cli/HEALTH_CLI_Coverage.md`
- `docs/cli/archive/SYNC_CLI_Development_State_archive_2025-12.md`
- `docs/cli/archive/SYNC_CLI_State_Archive_2025-12.md`
- `docs/cli/archive/SYNC_archive_2024-12.md`
- `docs/cli/commands/IMPLEMENTATION_Agents_Command.md`
- `docs/cli/commands/IMPLEMENTATION_Events_Command.md`
- `docs/cli/commands/IMPLEMENTATION_Tasks_Command.md`
- `docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md`
- `docs/cli/core/BEHAVIORS_CLI_Command_Effects.md`
- `docs/cli/core/HEALTH_CLI_Command_Test_Coverage.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/runtime/IMPLEMENTATION_Runtime_And_Dependencies.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/schema/IMPLEMENTATION_Schema.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/structure/IMPLEMENTATION_Code_Structure.md`
- `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`
- `docs/cli/core/SYNC_CLI_Development_State.md`
- `docs/cli/core/VALIDATION_CLI_Instruction_Invariants.md`
- `docs/cli/prompt/ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md`
- `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`
- `docs/cli/prompt/PATTERNS_Prompt_Command_Workflow_Design.md`
- `docs/cli/prompt/SYNC_Prompt_Command_State.md`
- `docs/connectome/PATTERNS_Connectome.md`
- `docs/core_utils/ALGORITHM_Core_Utils_Template_Path_And_Module_Discovery.md`
- `docs/core_utils/ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md`
- `docs/core_utils/PATTERNS_Core_Utils_Functions.md`
- `docs/infrastructure/api/ALGORITHM_Api.md`
- `docs/infrastructure/api/ALGORITHM_Playthrough_Creation.md`
- `docs/infrastructure/api/API_Graph_Management.md`
- `docs/infrastructure/api/BEHAVIORS_Api.md`
- `docs/infrastructure/api/IMPLEMENTATION_Api.md`
- `docs/infrastructure/api/PATTERNS_Api.md`
- `docs/infrastructure/api/SYNC_Api.md`
- `docs/infrastructure/api/TEST_Api.md`
- `docs/infrastructure/api/VALIDATION_Api.md`
- `docs/infrastructure/canon/PATTERNS_Canon.md`
- `docs/infrastructure/tempo/ALGORITHM_Tempo_Controller.md`
- `docs/infrastructure/tempo/IMPLEMENTATION_Tempo.md`
- `docs/infrastructure/tempo/PATTERNS_Tempo.md`
- `docs/ingest/PATTERNS_Doc_Ingestion.md`
- `docs/ingest/PATTERNS_File_Ingestion.md`
- `docs/ingest/PATTERNS_Graph_Injection.md`
- `docs/llm_agents/ALGORITHM_Gemini_Stream_Flow.md`
- `docs/llm_agents/BEHAVIORS_Gemini_Agent_Output.md`
- `docs/llm_agents/HEALTH_LLM_Agent_Coverage.md`
- `docs/llm_agents/IMPLEMENTATION_LLM_Agent_Code_Architecture.md`
- `docs/llm_agents/PATTERNS_Provider_Specific_LLM_Subprocesses.md`
- `docs/llm_agents/SYNC_LLM_Agents_State.md`
- `docs/llm_agents/SYNC_LLM_Agents_State_archive_2025-12.md`
- `docs/llm_agents/VALIDATION_Gemini_Agent_Invariants.md`
- `docs/membrane/IMPLEMENTATION_Membrane_System.md`
- `docs/membrane/VALIDATION_Completion_Verification.md`
- `docs/mind/models/HEALTH_Models.md`
- `docs/mind/models/PATTERNS_Models.md`
- `docs/mind/models/VALIDATION_Models.md`
- `docs/mind_cli_core/OBJECTIVES_mind_cli_core.md`
- `docs/mind_cli_core/PATTERNS_mind_cli_core.md`
- `docs/mind_cli_core/SYNC_mind_cli_core.md`
- `docs/physics/ALGORITHM_Physics.md`
- `docs/physics/BEHAVIORS_Physics.md`
- `docs/physics/DESIGN_Traversal_Logger.md`
- `docs/physics/EXAMPLE_Traversal_Log.md`
- `docs/physics/HEALTH_Energy_Physics.md`
- `docs/physics/IMPLEMENTATION_Physics.md`
- `docs/physics/PATTERNS_Physics.md`
- `docs/physics/SYNC_Physics.md`
- `docs/physics/SYNC_Physics_archive_2025-12.md`
- `docs/physics/TEST_Physics.md`
- `docs/physics/VALIDATION_Energy_Physics.md`
- `docs/physics/VALIDATION_Physics.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Mechanisms.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.1_Energy_Physics.md`
- `docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`
- `docs/physics/attention/PATTERNS_Attention_Energy_Split.md`
- `docs/physics/attention/VALIDATION_Attention_Split_And_Interrupts.md`
- `docs/physics/graph/ALGORITHM_Energy_Flow.md`
- `docs/physics/graph/ALGORITHM_Weight.md`
- `docs/physics/graph/BEHAVIORS_Graph.md`
- `docs/physics/graph/PATTERNS_Graph.md`
- `docs/physics/graph/SYNC_Graph.md`
- `docs/physics/graph/SYNC_Graph_archive_2025-12.md`
- `docs/physics/graph/VALIDATION_Living_Graph.md`
- `docs/physics/mechanisms/MECHANISMS_Awareness_Depth_Breadth.md`
- `docs/physics/subentity/ALGORITHM_SubEntity.md`
- `docs/physics/subentity/BEHAVIORS_SubEntity.md`
- `docs/physics/subentity/SYNC_SubEntity.md`
- `docs/physics/subentity/VALIDATION_SubEntity.md`
- `docs/physics/traversal_logger/IMPLEMENTATION_Traversal_Logger.md`
- `docs/runtime/membrane/BEHAVIORS_Membrane_Modulation.md`
- `docs/runtime/membrane/PATTERNS_Membrane_Modulation.md`
- `docs/runtime/membrane/PATTERNS_Membrane_Scoping.md`
- `docs/runtime/membrane/PATTERN_Membrane_Modulation.md`
- `docs/runtime/membrane/SYNC_Membrane_Modulation.md`
- `docs/runtime/models/HEALTH_Models.md`
- `docs/runtime/models/PATTERNS_Models.md`
- `docs/runtime/models/VALIDATION_Models.md`
- `docs/runtime/moments/PATTERNS_Moments.md`
- `docs/runtime/moments/SYNC_Moments.md`
- `docs/schema/GRAMMAR_Link_Synthesis.md`
- `docs/schema/PATTERNS_Schema.md`
- `docs/schema/SCHEMA.md`
- `docs/schema/SCHEMA_Moments.md`
- `docs/schema/SYNC_Schema.md`
- `docs/schema/models/PATTERNS_Pydantic_Schema_Models.md`
- `docs/tools/ALGORITHM_Tools.md`
- `docs/tools/BEHAVIORS_Tools.md`
- `docs/tools/HEALTH_Tools.md`
- `docs/tools/IMPLEMENTATION_Tools.md`
- `docs/tools/OBJECTIVES_Tools_Goals.md`
- `docs/tools/PATTERNS_Tools.md`
- `docs/tools/SYNC_Tools.md`
- `docs/tools/VALIDATION_Tools.md`
- `docs/tui/ALGORITHM_TUI_Widget_Interaction_Flow.md`
- `docs/tui/HEALTH_TUI_Coverage.md`
- `docs/tui/PATTERNS_TUI_Modular_Interface_Design.md`
- `implementation/IMPLEMENTATION_Physics_Architecture.md`
- `implementation/IMPLEMENTATION_Physics_Code_Structure.md`
- `implementation/IMPLEMENTATION_Physics_Dataflow.md`
- `implementation/IMPLEMENTATION_Physics_Runtime.md`
- `state/SYNC_Project_State.md`
- `templates/CLAUDE_ADDITION.md`
- `templates/CODEX_SYSTEM_PROMPT_ADDITION.md`
- `templates/mind/PRINCIPLES.md`
- `templates/mind/PROTOCOL.md`
- `templates/mind/agents/manager/CLAUDE.md`
- `templates/runtime/PRINCIPLES.md`
- `templates/runtime/PROTOCOL.md`
- `templates/runtime/agents/manager/CLAUDE.md`
- `tools/HEALTH_Tools.md`

**Sections:**
- # Repository Map: mind-mcp
