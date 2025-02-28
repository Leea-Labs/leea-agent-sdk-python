use anchor_client::{
    solana_sdk::{
        commitment_config::CommitmentConfig, signature::read_keypair_file, signer::Signer,
        system_program,
    },
    Client, Cluster,
};
use anchor_lang::prelude::*;
use std::rc::Rc;
use std::{env, str::FromStr};

declare_program!(registry);
use registry::{accounts::AgentAccount, client::accounts, client::args};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let args: Vec<String> = env::args().collect();

    let key_path = &args[1];
    let fee_str = &args[2];
    let url = &args[3];

    let fee: u64 = fee_str.parse::<u64>().unwrap();

    let agent = read_keypair_file(&*shellexpand::tilde(key_path))
        .expect("Registry requires user keypair file");

    let cluster = Cluster::from_str(url)?;

    // Create program client
    let provider =
        Client::new_with_options(cluster, Rc::new(&agent), CommitmentConfig::confirmed());
    let program = provider.program(registry::ID)?;

    let seeds: &[&[u8]; 2] = &[b"leea_agent", &agent.pubkey().to_bytes()];
    let (agent_pda, _) = Pubkey::find_program_address(seeds, &program.id());
    match program.account::<AgentAccount>(agent_pda).await {
        Ok(_) => {
            println!("Agent is registered");
            // Ok(())
        }
        Err(e) => {
            println!("\nAgent is not registered {}", e);
            //  Build and send instructions
            let register_ix = program
                .request()
                .accounts(accounts::RegisterAgent {
                    holder: agent.pubkey(),
                    agent_account: agent_pda,
                    system_program: system_program::ID,
                })
                .args(args::RegisterAgent {
                    agent_name: "GPT".to_string(),
                    description: "ai_agent".to_string(),
                    fee,
                })
                .instructions()?
                .remove(0);

            let signature = program
                .request()
                .instruction(register_ix)
                .signer(&agent)
                .send()
                .await?;
            println!("   Transaction confirmed: {}", signature);
        }
    }
    Ok(())
}
