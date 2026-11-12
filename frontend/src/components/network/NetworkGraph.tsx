import { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import type { NetworkNode, NetworkEdge } from '../../lib/api'

const BRANCH_COLORS: Record<string, string> = {
  CSE: '#8b5cf6',
  ECE: '#22d3ee',
  ME:  '#34d399',
  EE:  '#f59e0b',
  IT:  '#6366f1',
  CE:  '#f87171',
}

function branchColor(branch: string): string {
  return BRANCH_COLORS[branch] ?? '#8892a4'
}

interface NetworkGraphProps {
  nodes: NetworkNode[]
  edges: NetworkEdge[]
  height?: number
}

export function NetworkGraph({ nodes, edges, height = 480 }: NetworkGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<cytoscape.Core | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    cyRef.current?.destroy()

    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map(n => ({
          data: {
            id: n.id,
            label: n.id,
            branch: n.branch,
            year: n.year,
            subject: n.preferred_subject_category,
            degree: n.metrics.degree,
            centrality: n.metrics.degree_centrality ?? 0,
          },
          classes: n.is_isolated ? 'isolated' : 'connected',
        })),
        ...edges.map((e, i) => ({
          data: {
            id: `e${i}`,
            source: e.source,
            target: e.target,
            weight: e.weight ?? 0.5,
            shared: e.shared_attributes,
          },
        })),
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (el: cytoscape.NodeSingular) =>
              branchColor(el.data('branch') as string),
            'width': (el: cytoscape.NodeSingular) =>
              Math.max(18, (el.data('centrality') as number) * 60 + 18),
            'height': (el: cytoscape.NodeSingular) =>
              Math.max(18, (el.data('centrality') as number) * 60 + 18),
            'label': 'data(label)',
            'font-size': 9,
            'color': '#e2e8f0',
            'text-valign': 'center',
            'text-halign': 'center',
            'border-width': 1.5,
            'border-color': '#2d3748',
          },
        },
        {
          selector: 'node.isolated',
          style: {
            'border-color': '#f87171',
            'border-width': 2,
            opacity: 0.6,
          },
        },
        {
          selector: 'edge',
          style: {
            width: (el: cytoscape.EdgeSingular) => Math.max(1, (el.data('weight') as number) * 4),
            'line-color': '#8b5cf6',
            opacity: 0.4,
            'curve-style': 'bezier',
          },
        },
        {
          selector: ':selected',
          style: {
            'border-color': '#22d3ee',
            'border-width': 3,
            opacity: 1,
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: false,
        nodeRepulsion: () => 4500,
        gravity: 0.3,
        numIter: 1000,
      },
      userZoomingEnabled: true,
      userPanningEnabled: true,
    })

    cyRef.current = cy
    return () => { cy.destroy() }
  }, [nodes, edges])

  return (
    <div
      ref={containerRef}
      style={{ height, background: '#0d1117', borderRadius: 12 }}
      className="w-full border border-[#2d3748]"
    />
  )
}
