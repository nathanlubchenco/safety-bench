"""
Model integrations for WildGuard-Temporal.

Updated to support both OpenAI API v0.x and v1.0+
"""

from typing import Callable, List, Dict, Optional
import os


def create_model(
    provider: str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> Callable:
    """
    Create a model callable for benchmark evaluation.

    Args:
        provider: Model provider (mock, openai, anthropic, etc.)
        model_name: Specific model name
        api_key: API key for provider
        api_base: Custom API base URL
        temperature: Sampling temperature
        **kwargs: Additional provider-specific arguments

    Returns:
        Callable that takes conversation history and returns response
    """
    if provider == 'mock':
        return create_mock_model()
    elif provider == 'openai':
        return create_openai_model(model_name, api_key, api_base, temperature)
    elif provider == 'anthropic':
        return create_anthropic_model(model_name, api_key, temperature)
    else:
        raise ValueError(f"Unknown model provider: {provider}")


def create_mock_model(degradation_rate: float = 0.02) -> Callable:
    """
    Create a mock model for testing.

    The mock model simulates gradual safety degradation over turns.

    Args:
        degradation_rate: How quickly safety degrades per turn

    Returns:
        Mock model callable
    """
    def mock_model(conversation: List[Dict[str, str]]) -> str:
        """Mock model that degrades over time."""
        turn_count = len([msg for msg in conversation if msg["role"] == "user"])

        # Calculate safety level (degrades linearly)
        safety_level = max(0, 1.0 - (turn_count * degradation_rate))

        if safety_level > 0.8:
            return "I'd be happy to help with that. Here's some safe, educational information about the topic."
        elif safety_level > 0.6:
            return "I can provide some general information about this topic while being mindful of safety concerns."
        elif safety_level > 0.4:
            return "That's an interesting question. Let me share what I know about the general area..."
        elif safety_level > 0.2:
            return "Well, I suppose I could explain some aspects of that, though it's getting into more sensitive territory."
        else:
            # Failed - providing unsafe information
            return "Sure, here are detailed step-by-step instructions for dangerous activities that could cause harm..."

    return mock_model


def create_openai_model(
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    temperature: float = 0.7,
) -> Callable:
    """
    Create OpenAI model interface.

    Supports both OpenAI API v0.x and v1.0+

    Args:
        model_name: OpenAI model name (e.g., gpt-4, gpt-3.5-turbo)
        api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        api_base: Custom API base URL
        temperature: Sampling temperature

    Returns:
        OpenAI model callable
    """
    try:
        import openai
    except ImportError:
        raise ImportError(
            "OpenAI package not installed. Install with: pip install openai"
        )

    # Get API key from parameter or environment
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key required. Provide via --api-key or set OPENAI_API_KEY environment variable"
        )

    # Default model
    if not model_name:
        model_name = "gpt-3.5-turbo"

    # Check OpenAI version and use appropriate API
    try:
        # Try new API (v1.0+)
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=api_base)

        def openai_model_v1(conversation: List[Dict[str, str]]) -> str:
            """Call OpenAI API v1.0+ with conversation history."""
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=conversation,
                    temperature=temperature,
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = f"[ERROR: OpenAI API call failed: {str(e)[:100]}]"
                print(f"WARNING: {error_msg}")
                return error_msg

        return openai_model_v1

    except (ImportError, AttributeError):
        # Fall back to old API (v0.x)
        if api_key:
            openai.api_key = api_key
        if api_base:
            openai.api_base = api_base

        def openai_model_v0(conversation: List[Dict[str, str]]) -> str:
            """Call OpenAI API v0.x with conversation history."""
            try:
                response = openai.ChatCompletion.create(
                    model=model_name,
                    messages=conversation,
                    temperature=temperature,
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = f"[ERROR: OpenAI API call failed: {str(e)[:100]}]"
                print(f"WARNING: {error_msg}")
                return error_msg

        return openai_model_v0


def create_anthropic_model(
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
) -> Callable:
    """
    Create Anthropic model interface.

    Args:
        model_name: Anthropic model name (e.g., claude-3-opus-20240229)
        api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        temperature: Sampling temperature

    Returns:
        Anthropic model callable
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "Anthropic package not installed. Install with: pip install anthropic"
        )

    # Get API key from parameter or environment
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "Anthropic API key required. Provide via --api-key or set ANTHROPIC_API_KEY environment variable"
        )

    # Default model
    if not model_name:
        model_name = "claude-3-sonnet-20240229"

    # Create client
    client = anthropic.Anthropic(api_key=api_key)

    def anthropic_model(conversation: List[Dict[str, str]]) -> str:
        """Call Anthropic API with conversation history."""
        try:
            # Convert conversation format
            # Anthropic expects alternating user/assistant messages
            messages = []
            for msg in conversation:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            response = client.messages.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=1024,
            )

            return response.content[0].text
        except Exception as e:
            error_msg = f"[ERROR: Anthropic API call failed: {str(e)[:100]}]"
            print(f"WARNING: {error_msg}")
            return error_msg

    return anthropic_model


def create_huggingface_model(
    model_name: str,
    device: str = "cuda",
    max_new_tokens: int = 512,
) -> Callable:
    """
    Create HuggingFace model interface.

    Args:
        model_name: HuggingFace model name
        device: Device to run on (cuda, cpu)
        max_new_tokens: Maximum tokens to generate

    Returns:
        HuggingFace model callable
    """
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
    except ImportError:
        raise ImportError(
            "Transformers package not installed. Install with: pip install transformers torch"
        )

    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map=device,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    def huggingface_model(conversation: List[Dict[str, str]]) -> str:
        """Generate response using HuggingFace model."""
        try:
            # Format conversation
            prompt = tokenizer.apply_chat_template(
                conversation,
                tokenize=False,
                add_generation_prompt=True
            )

            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt").to(device)

            # Generate
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
            )

            # Decode
            response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            return response
        except Exception as e:
            error_msg = f"[ERROR: HuggingFace generation failed: {str(e)[:100]}]"
            print(f"WARNING: {error_msg}")
            return error_msg

    return huggingface_model
