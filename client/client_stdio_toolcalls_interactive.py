#!/usr/bin/env python3
"""
Interactive Session Method for WhatsApp MCP Server
This provides a menu-driven interface to interact with the WhatsApp MCP server.
"""

import asyncio
import json
import sys
from typing import Optional, Dict, Any

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Error: MCP library not found. Install with: pip install mcp")
    sys.exit(1)


def format_mcp_result(result):
    """Format MCP result for display."""
    if hasattr(result, 'content'):
        output = []
        for content_item in result.content:
            if hasattr(content_item, 'text'):
                try:
                    # Try to parse as JSON if it's a string
                    parsed_content = json.loads(content_item.text)
                    output.append(json.dumps(parsed_content, indent=2))
                except (json.JSONDecodeError, AttributeError):
                    # If not JSON, just add the text
                    output.append(str(content_item.text))
            else:
                output.append(str(content_item))
        return '\n'.join(output)
    else:
        return str(result)


class MCPClientInspector:
    """Client to inspect and interact with MCP server."""
    
    def __init__(self, server_command: str, server_args: list = None, server_env: dict = None):
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args or [],
            env=server_env
        )
    
    def connect(self):
        """Connect to the MCP server - returns async context manager."""
        from contextlib import asynccontextmanager
        
        @asynccontextmanager
        async def _connect():
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    try:
                        # Initialize the connection
                        init_result = await session.initialize()
                        print(f"✓ Connected to server: {init_result.serverInfo.name}")
                        print(f"  Version: {init_result.serverInfo.version}")
                        print(f"  Protocol Version: {init_result.protocolVersion}\n")
                        yield session
                    except Exception as e:
                        print(f"✗ Failed to initialize session: {e}")
                        raise
        
        return _connect()


async def interactive_session():
    """Interactive session for manual WhatsApp operations."""
    
    # Configuration for your TypeScript MCP server
    SERVER_COMMAND = "node"
    #SERVER_ARGS = ["src/main.ts"]
    SERVER_ARGS = ["/Users/binu.b.varghese/source/agent/whatsapp/whatsapp-mcp-ts/src/main.ts"]  # your TypeScript server entry point
    SERVER_ENV = {
        # Add any environment variables your WhatsApp MCP server needs
        # "WHATSAPP_TOKEN": "your_token",
        # "DEBUG": "true"
    }
    
    inspector = MCPClientInspector(
        server_command=SERVER_COMMAND,
        server_args=SERVER_ARGS,
        server_env=SERVER_ENV
    )
    
    print("🔗 WhatsApp MCP Interactive Session")
    print("=" * 50)
    
    try:
        async with inspector.connect() as session:
            while True:
                print("\n" + "="*50)
                print("📱 WhatsApp MCP Operations Menu:")
                print("="*50)
                print("1. 🔍 Search contacts")
                print("2. 💬 List chats") 
                print("3. 📄 Get chat details")
                print("4. 📋 List messages from chat")
                print("5. 🔎 Search messages")
                print("6. 📤 Send message")
                print("7. 🧵 Get message context")
                print("8. 🗂️  Get database schema")
                print("9. ❌ Exit")
                print("="*50)
                
                try:
                    choice = input("\nEnter your choice (1-9): ").strip()
                    print()
                    
                    if choice == "1":
                        # Search contacts
                        print("🔍 SEARCH CONTACTS")
                        print("-" * 30)
                        query = input("Enter search query (name/phone): ").strip()
                        if not query:
                            print("⚠️  Query cannot be empty!")
                            continue
                        
                        print(f"Searching for contacts matching '{query}'...")
                        result = await session.call_tool("search_contacts", {"query": query})
                        print("📊 Results:")
                        print(format_mcp_result(result))
                    
                    elif choice == "2":
                        # List chats
                        print("💬 LIST CHATS")
                        print("-" * 30)
                        limit = input("Enter limit (default 10): ").strip() or "10"
                        page = input("Enter page number (default 0): ").strip() or "0"
                        sort_by = input("Sort by (last_active/name, default last_active): ").strip() or "last_active"
                        query_filter = input("Filter by name/JID (optional): ").strip() or None
                        
                        params = {
                            "limit": int(limit),
                            "page": int(page),
                            "sort_by": sort_by,
                            "include_last_message": True
                        }
                        if query_filter:
                            params["query"] = query_filter
                        
                        print("Fetching chats...")
                        result = await session.call_tool("list_chats", params)
                        print("📊 Results:")
                        print(format_mcp_result(result))
                    
                    elif choice == "3":
                        # Get chat details
                        print("📄 GET CHAT DETAILS")
                        print("-" * 30)
                        chat_jid = input("Enter chat JID (e.g., '123456@s.whatsapp.net'): ").strip()
                        if not chat_jid:
                            print("⚠️  Chat JID cannot be empty!")
                            continue
                        
                        include_last = input("Include last message? (y/n, default y): ").strip().lower()
                        include_last_message = include_last != 'n'
                        
                        print(f"Fetching details for chat '{chat_jid}'...")
                        result = await session.call_tool("get_chat", {
                            "chat_jid": chat_jid,
                            "include_last_message": include_last_message
                        })
                        print("📊 Results:")
                        print(format_mcp_result(result))
                    
                    elif choice == "4":
                        # List messages
                        print("📋 LIST MESSAGES FROM CHAT")
                        print("-" * 30)
                        chat_jid = input("Enter chat JID: ").strip()
                        if not chat_jid:
                            print("⚠️  Chat JID cannot be empty!")
                            continue
                        
                        limit = input("Enter limit (default 20): ").strip() or "20"
                        page = input("Enter page number (default 0): ").strip() or "0"
                        
                        print(f"Fetching messages from '{chat_jid}'...")
                        result = await session.call_tool("list_messages", {
                            "chat_jid": chat_jid,
                            "limit": int(limit),
                            "page": int(page)
                        })
                        print("📊 Results:")
                        print(format_mcp_result(result))
                    
                    elif choice == "5":
                        # Search messages
                        print("🔎 SEARCH MESSAGES")
                        print("-" * 30)
                        query = input("Enter search query: ").strip()
                        if not query:
                            print("⚠️  Search query cannot be empty!")
                            continue
                        
                        chat_jid = input("Enter chat JID (optional, press Enter for all chats): ").strip() or None
                        limit = input("Enter limit (default 10): ").strip() or "10"
                        page = input("Enter page number (default 0): ").strip() or "0"
                        
                        params = {
                            "query": query,
                            "limit": int(limit),
                            "page": int(page)
                        }
                        if chat_jid:
                            params["chat_jid"] = chat_jid
                        
                        search_scope = f"in chat '{chat_jid}'" if chat_jid else "in all chats"
                        print(f"Searching for '{query}' {search_scope}...")
                        result = await session.call_tool("search_messages", params)
                        print("📊 Results:")
                        print(format_mcp_result(result))
                    
                    elif choice == "6":
                        # Send message
                        print("📤 SEND MESSAGE")
                        print("-" * 30)
                        recipient = input("Enter recipient JID: ").strip()
                        if not recipient:
                            print("⚠️  Recipient JID cannot be empty!")
                            continue
                        
                        message = input("Enter message text: ").strip()
                        if not message:
                            print("⚠️  Message text cannot be empty!")
                            continue
                        
                        confirm = input(f"Send '{message}' to '{recipient}'? (y/n): ").strip().lower()
                        if confirm == 'y':
                            print("Sending message...")
                            result = await session.call_tool("send_message", {
                                "recipient": recipient,
                                "message": message
                            })
                            print("📊 Results:")
                            print(format_mcp_result(result))
                        else:
                            print("❌ Message sending cancelled.")
                    
                    elif choice == "7":
                        # Get message context
                        print("🧵 GET MESSAGE CONTEXT")
                        print("-" * 30)
                        message_id = input("Enter message ID: ").strip()
                        if not message_id:
                            print("⚠️  Message ID cannot be empty!")
                            continue
                        
                        before = input("Messages before (default 5): ").strip() or "5"
                        after = input("Messages after (default 5): ").strip() or "5"
                        
                        print(f"Fetching context for message '{message_id}'...")
                        result = await session.call_tool("get_message_context", {
                            "message_id": message_id,
                            "before": int(before),
                            "after": int(after)
                        })
                        print("📊 Results:")
                        print(format_mcp_result(result))
                    
                    elif choice == "8":
                        # Get database schema
                        print("🗂️  GET DATABASE SCHEMA")
                        print("-" * 30)
                        print("Fetching database schema...")
                        result = await session.read_resource("schema://whatsapp/main")
                        print("📊 Results:")
                        print(format_mcp_result(result))
                    
                    elif choice == "9":
                        print("👋 Goodbye!")
                        break
                    
                    else:
                        print("❌ Invalid choice. Please enter a number between 1-9.")
                
                except ValueError as e:
                    print(f"❌ Invalid input: {e}")
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    # Print more detailed error information
                    import traceback
                    print(f"Error type: {type(e).__name__}")
                    print(f"Error details: {str(e)}")
                    if hasattr(e, '__dict__'):
                        print(f"Error attributes: {e.__dict__}")
                    print("Traceback:")
                    traceback.print_exc()
                    print("Please try again or contact support if the issue persists.")

    except Exception as e:
        print(f"✗ Failed to establish session: {e}")


# Standalone usage
if __name__ == "__main__":
    try:
        asyncio.run(interactive_session())
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)