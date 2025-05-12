from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers.
    
    Args:
        a: The first number to add
        b: The second number to add
        
    Returns:
        The sum of a and b
        
    Examples:
        To add 5 and 3, provide a=5, b=3
    """
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.
    
    Args:
        a: The first number to multiply
        b: The second number to multiply
        
    Returns:
        The product of a and b
        
    Examples:
        To multiply 5 and 3, provide a=5, b=3. Do not use expressions like "5*3".
    """
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")
