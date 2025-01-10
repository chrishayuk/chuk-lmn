import logging
logger = logging.getLogger(__name__)

class ContinueEmitter:
    def __init__(self, controller):
        self.controller = controller

    def emit_continue(self, node, out_lines):
        """
        node might look like:
          {
            "type": "ContinueStatement",
            "loop_var_name": "i",   # potentially added by ForEmitter
            "step_expr": <AST or None>
          }
        
        But in your ForEmitter design, the post-body increment
        is done outside the block $for_continue, so we simply
        branch there to skip further statements in the loop body.
        """
        # If you want to rely purely on the for-emitter’s 'block $for_continue' logic,
        # no manual increment is needed here:
        logger.debug("ContinueEmitter: Emitting 'continue' => br $for_continue")

        # Just branch to skip the rest of the loop body:
        out_lines.append("  br $for_continue")
